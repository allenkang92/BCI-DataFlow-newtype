"""
API 엔드포인트를 정의하는 모듈입니다.
"""

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional

from app.security.security import SecurityConfig, Token, User
from app.schemas.data_validation import EEGDataPoint, EEGDataset
from app.monitoring.model_monitor import ModelMonitor
from app.monitoring.system_monitor import SystemMonitor
from app.experimentation.ab_testing import ABTest, Experiment

# API 라우터 설정
router = APIRouter()

# 보안 설정
security_config = SecurityConfig(secret_key="your-secret-key")  # TODO: 환경 변수에서 로드

# 모니터링 설정
model_monitor = ModelMonitor(model_version="v1", metrics_path="metrics/model_metrics.json")
system_monitor = SystemMonitor(metrics_path="metrics/system_metrics.json")

# A/B 테스트 설정
experiment = Experiment(
    name="model_comparison",
    variant_a="model_v1",
    variant_b="model_v2",
    traffic_split=0.5
)
ab_test = ABTest(experiment, results_path="metrics/ab_test_results.json")

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """액세스 토큰을 발급합니다."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security_config.create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes}
    )
    return Token(access_token=access_token, token_type="bearer")

@router.post("/predict")
async def predict(
    data: EEGDataPoint,
    current_user: User = Depends(security_config.get_current_active_user)
) -> dict:
    """EEG 데이터에 대한 예측을 수행합니다.

    Args:
        data: EEG 데이터 포인트
        current_user: 현재 사용자 정보

    Returns:
        예측 결과
    """
    try:
        # A/B 테스트를 위한 변형 할당
        variant = ab_test.assign_variant(str(current_user.id))
        
        # 예측 수행
        start_time = time.time()
        prediction = perform_prediction(data, variant)
        latency = time.time() - start_time

        # 모니터링 메트릭 기록
        model_monitor.log_prediction(
            prediction=prediction,
            true_value=None,
            features=data.dict(),
            latency=latency
        )

        return {
            "prediction": prediction,
            "variant": variant,
            "latency": latency
        }

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/feedback")
async def record_feedback(
    data: EEGDataPoint,
    true_value: int,
    current_user: User = Depends(security_config.get_current_active_user)
) -> dict:
    """예측에 대한 피드백을 기록합니다.

    Args:
        data: EEG 데이터 포인트
        true_value: 실제 값
        current_user: 현재 사용자 정보

    Returns:
        처리 결과
    """
    try:
        variant = ab_test.assign_variant(str(current_user.id))
        
        # 예측 수행 및 피드백 기록
        start_time = time.time()
        prediction = perform_prediction(data, variant)
        latency = time.time() - start_time

        # A/B 테스트 결과 기록
        ab_test.log_prediction(
            variant=variant,
            prediction=prediction,
            true_value=true_value
        )

        # 모델 모니터링 메트릭 기록
        model_monitor.log_prediction(
            prediction=prediction,
            true_value=true_value,
            features=data.dict(),
            latency=latency
        )

        return {
            "status": "success",
            "recorded": {
                "prediction": prediction,
                "true_value": true_value,
                "variant": variant
            }
        }

    except Exception as e:
        logger.error(f"Failed to record feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/metrics/model")
async def get_model_metrics(
    current_user: User = Security(
        security_config.get_current_active_user,
        scopes=["admin"]
    )
) -> dict:
    """모델 성능 메트릭을 조회합니다.

    Args:
        current_user: 현재 사용자 정보 (관리자 권한 필요)

    Returns:
        모델 성능 메트릭
    """
    return model_monitor.get_metrics_summary()

@router.get("/metrics/system")
async def get_system_metrics(
    current_user: User = Security(
        security_config.get_current_active_user,
        scopes=["admin"]
    )
) -> dict:
    """시스템 메트릭을 조회합니다.

    Args:
        current_user: 현재 사용자 정보 (관리자 권한 필요)

    Returns:
        시스템 메트릭
    """
    return system_monitor.get_metrics_summary()

@router.get("/experiment/results")
async def get_experiment_results(
    current_user: User = Security(
        security_config.get_current_active_user,
        scopes=["admin"]
    )
) -> dict:
    """A/B 테스트 결과를 조회합니다.

    Args:
        current_user: 현재 사용자 정보 (관리자 권한 필요)

    Returns:
        실험 결과 및 분석
    """
    analysis = ab_test.analyze_results()
    recommendation = ab_test.get_recommendation()
    
    return {
        "analysis": analysis,
        "recommendation": recommendation
    }

@router.post("/dataset/validate")
async def validate_dataset(
    dataset: EEGDataset,
    current_user: User = Depends(security_config.get_current_active_user)
) -> dict:
    """데이터셋의 유효성을 검사합니다.

    Args:
        dataset: 검증할 EEG 데이터셋
        current_user: 현재 사용자 정보

    Returns:
        검증 결과
    """
    try:
        # 데이터셋의 각 데이터 포인트 검증
        invalid_points = []
        for i, data_point in enumerate(dataset.data):
            try:
                # Pydantic 모델이 자동으로 검증
                EEGDataPoint(**data_point.dict())
            except Exception as e:
                invalid_points.append({
                    "index": i,
                    "error": str(e)
                })

        if invalid_points:
            return {
                "valid": False,
                "invalid_points": invalid_points
            }
        
        return {
            "valid": True,
            "message": "All data points are valid"
        }

    except Exception as e:
        logger.error(f"Dataset validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

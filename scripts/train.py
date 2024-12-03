"""
EEG 데이터를 사용하여 머신러닝 모델을 학습하는 모듈입니다.

이 모듈은 전처리된 EEG 데이터를 입력받아 RandomForest 분류기를 학습하고,
MLflow를 통해 모델과 메트릭을 추적합니다.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.exceptions import NotFittedError
import mlflow
import mlflow.sklearn
import yaml
import os
import re
from datetime import datetime
from app.schemas.data_validation import EEGDataPoint
import json
import platform
import sklearn
import joblib

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelTrainingError(Exception):
    """모델 학습 중 발생하는 에러를 처리하기 위한 커스텀 예외 클래스"""
    pass

def extract_numbers(s: str) -> List[float]:
    """문자열에서 숫자 목록을 추출합니다.

    Args:
        s: 숫자가 포함된 문자열 (예: "[1.23, 4.56, 7.89]")

    Returns:
        추출된 숫자 목록

    Raises:
        ValueError: 숫자를 추출할 수 없는 경우
    """
    if not s:
        return []
    
    # Check if the string contains brackets
    if '[' not in s or ']' not in s:
        return []
        
    try:
        # 대괄호 제거 및 쉼표로 분리
        numbers_str = s.strip('[]').split(',')
        # 각 문자열을 float로 변환
        return [float(num.strip()) for num in numbers_str if num.strip()]
    except (ValueError, AttributeError) as e:
        logger.error(f"Failed to extract numbers from string: {s}")
        return []  # Return empty list instead of raising error for invalid input

def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    """데이터의 유효성을 검사하고 필요한 전처리를 수행합니다.

    Args:
        data (pd.DataFrame): 검증할 데이터프레임

    Returns:
        pd.DataFrame: 검증과 전처리가 완료된 데이터프레임

    Raises:
        ValueError: 데이터가 유효하지 않은 경우
    """
    if data.empty:
        raise ValueError("데이터가 비어 있습니다")

    required_columns = ['subject_id', 'run_id', 'preprocessed', 'channels', 'coordsystem', 'electrodes']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}")

    try:
        # subject_id를 정수형으로 변환
        data['subject_id'] = data['subject_id'].astype(int)
        
        # run_id 형식 검증 및 변환
        def validate_run_id(run_id):
            if isinstance(run_id, str) and run_id.startswith('run'):
                try:
                    num = int(run_id[3:])
                    return f'run{num}'
                except ValueError:
                    raise ValueError(f"잘못된 run_id 형식입니다: {run_id}. 'runX' 형식이어야 합니다 (X는 숫자)")
            elif isinstance(run_id, (int, float)):
                return f'run{int(run_id)}'
            else:
                raise ValueError(f"잘못된 run_id 형식입니다: {run_id}. 'runX' 형식이어야 합니다 (X는 숫자)")
        
        data['run_id'] = data['run_id'].apply(validate_run_id)

        # preprocessed 데이터가 문자열 형식인지 확인
        if not all(isinstance(x, str) for x in data['preprocessed']):
            raise ValueError("preprocessed 데이터는 문자열 형식이어야 합니다")

    except Exception as e:
        raise ValueError(f"데이터 타입 변환 중 오류가 발생했습니다: {str(e)}")

    return data

def detect_data_drift(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    threshold: float = 2.0,
    exclude_columns: List[str] = None,
    min_absolute_change: float = 1e-3,
    std_threshold: float = 0.2,  # 표준편차 임계값을 0.2로 증가
    zero_threshold: float = 0.5  # 0에 가까운 범위를 넓힘
) -> Tuple[bool, Dict[str, Dict[str, float]]]:
    """
    두 데이터셋 간의 드리프트를 감지합니다.

    Args:
        reference_data: 기준 데이터
        current_data: 현재 데이터
        threshold: 드리프트를 판단하는 상대적 차이의 임계값
        exclude_columns: 드리프트 검사에서 제외할 컬럼들
        min_absolute_change: 드리프트로 판단할 최소 절대 차이
        std_threshold: 표준편차 차이의 임계값
        zero_threshold: 평균이 0에 가까운지 판단하는 임계값

    Returns:
        (드리프트 존재 여부, 드리프트 정보)
    """
    if exclude_columns is None:
        exclude_columns = []

    drift_info = {}
    has_drift = False

    numeric_columns = reference_data.select_dtypes(include=[np.number]).columns
    numeric_columns = [col for col in numeric_columns if col not in exclude_columns]

    for column in numeric_columns:
        ref_mean = reference_data[column].mean()
        cur_mean = current_data[column].mean()
        ref_std = reference_data[column].std()
        cur_std = current_data[column].std()
        
        # 평균의 절대적 차이 계산
        mean_diff = abs(cur_mean - ref_mean)
        
        # 평균이 0에 가까운 경우와 그렇지 않은 경우를 구분하여 처리
        if abs(ref_mean) < zero_threshold:
            # 0에 가까운 경우, 절대적 차이를 사용하되 임계값을 더 크게 설정
            mean_relative_diff = mean_diff
            has_mean_drift = mean_diff > zero_threshold
        else:
            # 0에서 먼 경우, 상대적 차이를 사용
            mean_relative_diff = mean_diff / abs(ref_mean)
            has_mean_drift = mean_relative_diff > threshold

        # 표준편차의 상대적 차이 계산
        if ref_std > 1e-10:
            std_relative_diff = abs(cur_std - ref_std) / ref_std
        else:
            std_relative_diff = abs(cur_std - ref_std) if abs(cur_std - ref_std) > min_absolute_change else 0

        drift_info[column] = {
            'reference_mean': ref_mean,
            'current_mean': cur_mean,
            'reference_std': ref_std,
            'current_std': cur_std,
            'mean_difference': mean_diff,
            'std_difference': std_relative_diff,
            'mean_relative_difference': mean_relative_diff
        }

        # 드리프트 판단:
        # 1. 평균의 차이가 임계값을 초과하고
        # 2. 표준편차의 차이도 임계값을 초과할 때만 드리프트로 판단
        if has_mean_drift and std_relative_diff > std_threshold:
            has_drift = True

    return has_drift, drift_info

def train_model(
    data_path: Union[str, Path],
    model_output_path: Union[str, Path],
    hyperparameters_path: Union[str, Path],
    metrics_dir: Union[str, Path]
) -> None:
    """
    데이터를 사용하여 모델을 학습하고 평가합니다.

    Args:
        data_path: 학습 데이터 파일 경로
        model_output_path: 학습된 모델을 저장할 경로
        hyperparameters_path: 하이퍼파라미터 파일 경로
        metrics_dir: 메트릭을 저장할 디렉토리 경로
    """
    try:
        # 데이터 로드
        if not Path(data_path).exists():
            raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")

        data = pd.read_csv(data_path)
        
        # 데이터 검증
        try:
            validate_data(data)
        except ValueError as e:
            raise ModelTrainingError(f"데이터 검증 실패: {str(e)}")

        # 전처리된 데이터 추출
        try:
            X = np.array([extract_numbers(x) for x in data['preprocessed']])
            if len(X) == 0:
                raise ModelTrainingError("전처리된 데이터가 비어있거나 잘못된 형식입니다")
            if any(len(x) == 0 for x in X):
                raise ModelTrainingError("전처리된 데이터가 비어있거나 잘못된 형식입니다")
            if any(not isinstance(x, (list, np.ndarray)) for x in X):
                raise ModelTrainingError("전처리된 데이터가 비어있거나 잘못된 형식입니다")
        except (ValueError, TypeError) as e:
            raise ModelTrainingError("전처리된 데이터가 비어있거나 잘못된 형식입니다")

        y = data['events'].astype('category').cat.codes

        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # 하이퍼파라미터 로드
        try:
            with open(hyperparameters_path) as f:
                hyperparameters = yaml.safe_load(f)
        except Exception as e:
            raise ModelTrainingError(f"하이퍼파라미터 파일을 읽을 수 없습니다: {str(e)}")

        # 모델 학습
        with mlflow.start_run():
            model = RandomForestClassifier(**hyperparameters)
            model.fit(X_train, y_train)

            # 예측 및 메트릭 계산
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            # MLflow에 메트릭 기록
            train_metrics = {
                'train_accuracy': accuracy_score(y_train, y_train_pred),
                'train_precision': precision_score(y_train, y_train_pred, average='weighted', zero_division=0),
                'train_recall': recall_score(y_train, y_train_pred, average='weighted', zero_division=0),
                'train_f1': f1_score(y_train, y_train_pred, average='weighted', zero_division=0)
            }

            test_metrics = {
                'test_accuracy': accuracy_score(y_test, y_test_pred),
                'test_precision': precision_score(y_test, y_test_pred, average='weighted', zero_division=0),
                'test_recall': recall_score(y_test, y_test_pred, average='weighted', zero_division=0),
                'test_f1': f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
            }

            for name, value in {**train_metrics, **test_metrics}.items():
                mlflow.log_metric(name, value)

            # 모델 저장
            joblib.dump(model, model_output_path)
            mlflow.sklearn.log_model(model, "model")

    except FileNotFoundError as e:
        raise ModelTrainingError(str(e))
    except Exception as e:
        if not isinstance(e, ModelTrainingError):
            raise ModelTrainingError(f"모델 학습 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        data_path = '/code/data/processed/eeg_data.csv'
        model_output_path = '/code/models/model.pkl'
        hyperparameters_path = '/code/config/hyperparameters.yaml'
        metrics_dir = '/code/metrics'

        train_model(
            data_path=data_path,
            model_output_path=model_output_path,
            hyperparameters_path=hyperparameters_path,
            metrics_dir=metrics_dir
        )
        logger.info("Model training completed successfully")
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

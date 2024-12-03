"""
train.py 모듈에 대한 테스트 파일입니다.
"""

import pytest
import numpy as np
import pandas as pd
import json
import mlflow
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock, ANY
from scripts.train import (
    extract_numbers,
    validate_data,
    detect_data_drift,
    train_model,
    ModelTrainingError
)
from app.schemas.data_validation import EEGDataPoint

@pytest.fixture
def sample_data():
    """테스트를 위한 샘플 데이터를 생성합니다."""
    return pd.DataFrame({
        'preprocessed': [
            '[1.23e-06, 2.34e-06, 3.45e-06]',
            '[4.56e-06, 5.67e-06, 6.78e-06]',
            '[1.23e-06, 2.34e-06, 3.45e-06]',
            '[4.56e-06, 5.67e-06, 6.78e-06]',
            '[1.23e-06, 2.34e-06, 3.45e-06]',
            '[7.78e-06, 8.89e-06, 9.90e-06]'
        ],
        'subject_id': [1, 2, 1, 2, 1, 2],
        'run_id': ['run1', 'run2', 'run3', 'run4', 'run5', 'run6'],
        'channels': ['ch1,ch2,ch3'] * 6,
        'coordsystem': ['sys1'] * 6,
        'electrodes': ['e1,e2,e3'] * 6,
        'events': ['event' + str(i) for i in range(1, 7)]
    })

@pytest.fixture
def temp_files(tmp_path, sample_data):
    """테스트에 필요한 임시 파일들을 생성합니다."""
    data_path = tmp_path / "test_data.csv"
    model_output_path = tmp_path / "test_model.pkl"
    hyperparameters_path = tmp_path / "test_hyperparams.yaml"
    metrics_dir = tmp_path / "metrics"
    reference_data_path = tmp_path / "reference_data.csv"

    # 테스트 데이터 저장
    sample_data.to_csv(data_path, index=False)

    # 기준 데이터 생성 및 저장
    reference_data = sample_data.copy()
    reference_data.to_csv(reference_data_path, index=False)

    # 하이퍼파라미터 저장
    hyperparameters = {
        "n_estimators": 100,
        "max_depth": 5,
        "random_state": 42
    }
    with open(hyperparameters_path, 'w') as f:
        yaml.dump(hyperparameters, f)

    metrics_dir.mkdir(exist_ok=True)

    return {
        'data_path': str(data_path),
        'model_output_path': str(model_output_path),
        'hyperparameters_path': str(hyperparameters_path),
        'metrics_dir': str(metrics_dir),
        'reference_data_path': str(reference_data_path)
    }

@pytest.fixture
def reference_data():
    """데이터 드리프트 감지를 위한 참조 데이터를 생성합니다."""
    np.random.seed(42)
    n_samples = 100
    n_features = 3
    
    # 특성 데이터 생성
    feature_data = np.random.normal(loc=0, scale=1e-6, size=(n_samples, n_features))
    
    # DataFrame 생성
    data = pd.DataFrame(feature_data, columns=[f'feature_{i}' for i in range(n_features)])
    data['subject_id'] = np.random.randint(1, 3, size=n_samples)
    data['run_id'] = np.arange(1, n_samples + 1)
    
    return data

def test_extract_numbers():
    """숫자 추출 함수를 테스트합니다."""
    # 정상 케이스
    input_str = "[1.23e-06, 2.34e-06, 3.45e-06]"
    expected = [1.23e-06, 2.34e-06, 3.45e-06]
    assert extract_numbers(input_str) == expected
    
    # 빈 문자열
    assert extract_numbers("") == []
    
    # 숫자가 없는 경우
    assert extract_numbers("no numbers here") == []

def test_validate_data_with_invalid_types():
    """잘못된 데이터 타입에 대한 검증 테스트"""
    invalid_data = pd.DataFrame({
        'subject_id': ['not_an_int'],  # 정수가 아닌 값
        'run_id': ['not_a_number'],  # 숫자가 아닌 값
        'preprocessed': [123],  # 문자열이 아닌 값
        'channels': ['channel1'],
        'coordsystem': ['coord1'],
        'electrodes': ['elec1']
    })
    
    with pytest.raises(ValueError) as exc_info:
        validate_data(invalid_data)
    assert "데이터 타입 변환 중 오류가 발생했습니다" in str(exc_info.value)

def test_validate_data_with_missing_columns():
    """누락된 컬럼에 대한 검증 테스트"""
    incomplete_data = pd.DataFrame({
        'subject_id': [1],
        'run_id': ['run1'],  # validate_data에서 'runX' 형식으로 변환됨
        # preprocessed 컬럼 누락
    })
    
    with pytest.raises(ValueError) as exc_info:
        validate_data(incomplete_data)
    assert "필수 컬럼이 누락되었습니다" in str(exc_info.value)

def test_validate_data_with_empty_data():
    """빈 데이터에 대한 검증 테스트"""
    empty_data = pd.DataFrame()
    
    with pytest.raises(ValueError) as exc_info:
        validate_data(empty_data)
    assert "데이터가 비어 있습니다" in str(exc_info.value)

def test_validate_data_with_valid_data():
    """유효한 데이터에 대한 검증 테스트"""
    valid_data = pd.DataFrame({
        'subject_id': [1, 2],
        'run_id': ['run1', 'run2'],  # validate_data에서 'runX' 형식으로 변환됨
        'preprocessed': ['[1.23e-06, 2.34e-06, 3.45e-06]', '[4.56e-06, 5.67e-06, 6.78e-06]'],
        'channels': ['channel1', 'channel2'],
        'coordsystem': ['coord1', 'coord2'],
        'electrodes': ['elec1', 'elec2']
    })
    
    # 예외가 발생하지 않아야 함
    validate_data(valid_data)

def test_detect_data_drift():
    """데이터 드리프트 감지 함수를 테스트합니다."""
    np.random.seed(42)

    # 기준 데이터 생성 (평균 0, 표준편차 1)
    reference = pd.DataFrame({
        'feature_0': np.random.normal(0, 1, 100),
        'feature_1': np.random.normal(0, 1, 100),
        'feature_2': np.random.normal(0, 1, 100),
        'subject_id': [1] * 100,
        'run_id': [f'run{i}' for i in range(1, 101)]
    })

    # 드리프트가 없는 현재 데이터 (매우 비슷한 분포)
    current_no_drift = pd.DataFrame({
        'feature_0': np.random.normal(0, 1.05, 100),  # 표준편차를 약간만 다르게
        'feature_1': np.random.normal(0, 1.05, 100),
        'feature_2': np.random.normal(0, 1.05, 100),
        'subject_id': [1] * 100,
        'run_id': [f'run{i}' for i in range(1, 101)]
    })

    # 드리프트가 있는 현재 데이터 (매우 다른 분포)
    current_with_drift = pd.DataFrame({
        'feature_0': np.random.normal(10, 2, 100),  # 평균과 표준편차가 매우 다름
        'feature_1': np.random.normal(10, 2, 100),
        'feature_2': np.random.normal(10, 2, 100),
        'subject_id': [1] * 100,
        'run_id': [f'run{i}' for i in range(1, 101)]
    })

    # 드리프트가 없는 경우 테스트 (임계값 2.0으로 설정)
    has_drift, drift_info = detect_data_drift(reference, current_no_drift, threshold=2.0)
    print("\n드리프트가 없는 경우의 정보:", drift_info)
    assert not has_drift, "드리프트가 없어야 하는데 감지되었습니다"

    # 드리프트가 있는 경우 테스트
    has_drift, drift_info = detect_data_drift(reference, current_with_drift, threshold=2.0)
    print("\n드리프트가 있는 경우의 정보:", drift_info)
    assert has_drift, "드리프트가 있어야 하는데 감지되지 않았습니다"

@patch('mlflow.start_run')
@patch('mlflow.sklearn.log_model')
@patch('mlflow.log_params')
@patch('mlflow.log_metric')
def test_train_model(mock_log_metric, mock_log_params, mock_log_model, mock_start_run, temp_files):
    """모델 학습 함수를 테스트합니다."""
    # MLflow 컨텍스트 매니저 설정
    mock_run = MagicMock()
    mock_run.__enter__ = MagicMock(return_value=mock_run)
    mock_run.__exit__ = MagicMock(return_value=None)
    mock_start_run.return_value = mock_run

    # 모델 학습 실행
    train_model(
        data_path=temp_files['data_path'],
        model_output_path=temp_files['model_output_path'],
        hyperparameters_path=temp_files['hyperparameters_path'],
        metrics_dir=temp_files['metrics_dir']
    )

    # 메트릭이 기록되었는지 확인
    mock_log_metric.assert_any_call('train_accuracy', ANY)
    mock_log_metric.assert_any_call('test_accuracy', ANY)
    mock_log_metric.assert_any_call('train_precision', ANY)
    mock_log_metric.assert_any_call('test_precision', ANY)
    mock_log_metric.assert_any_call('train_recall', ANY)
    mock_log_metric.assert_any_call('test_recall', ANY)
    mock_log_metric.assert_any_call('train_f1', ANY)
    mock_log_metric.assert_any_call('test_f1', ANY)

def test_train_model_missing_file():
    """존재하지 않는 파일로 모델 학습을 시도할 때를 테스트합니다."""
    with pytest.raises(ModelTrainingError, match="데이터 파일을 찾을 수 없습니다"):
        train_model(
            data_path="nonexistent.csv",
            model_output_path="model.pkl",
            hyperparameters_path="hyperparams.yaml",
            metrics_dir="metrics"
        )

def test_train_model_invalid_data(temp_files, sample_data):
    """잘못된 데이터로 모델 학습을 시도할 때를 테스트합니다."""
    # 잘못된 데이터 생성
    invalid_data = sample_data.copy()
    invalid_data.loc[0, 'preprocessed'] = 'invalid_data'  # 잘못된 형식의 preprocessed 데이터

    # 잘못된 데이터를 파일에 저장
    invalid_data_file = Path(temp_files['data_path']).parent / "invalid_data.csv"
    invalid_data.to_csv(invalid_data_file, index=False)

    # MLflow 실행이 있다면 종료
    mlflow.end_run()

    # 잘못된 데이터로 모델 학습 시도
    with pytest.raises(ModelTrainingError, match="전처리된 데이터가 비어있거나 잘못된 형식입니다"):
        train_model(
            data_path=str(invalid_data_file),
            model_output_path=temp_files['model_output_path'],
            hyperparameters_path=temp_files['hyperparameters_path'],
            metrics_dir=temp_files['metrics_dir']
        )

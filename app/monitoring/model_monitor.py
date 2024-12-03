"""
모델 성능 모니터링을 위한 모듈입니다.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix
)
from prometheus_client import Counter, Gauge, Histogram

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus 메트릭 정의
PREDICTION_COUNTER = Counter(
    'model_predictions_total',
    'Total number of predictions made',
    ['model_version']
)
PREDICTION_LATENCY = Histogram(
    'model_prediction_latency_seconds',
    'Time spent processing predictions',
    ['model_version']
)
MODEL_ACCURACY = Gauge(
    'model_accuracy',
    'Current model accuracy',
    ['model_version']
)
DATA_DRIFT_SCORE = Gauge(
    'data_drift_score',
    'Current data drift score',
    ['feature']
)

class ModelMonitor:
    """모델 성능 모니터링을 위한 클래스"""

    def __init__(
        self,
        model_version: str,
        metrics_path: Union[str, Path],
        reference_data: Optional[pd.DataFrame] = None
    ):
        """
        Args:
            model_version: 모델 버전
            metrics_path: 메트릭을 저장할 경로
            reference_data: 데이터 드리프트 탐지를 위한 참조 데이터
        """
        self.model_version = model_version
        self.metrics_path = Path(metrics_path)
        self.reference_data = reference_data
        self.predictions_buffer: List[Dict] = []
        self.buffer_size = 100  # 버퍼 크기

    def log_prediction(
        self,
        prediction: Union[int, float],
        true_value: Optional[Union[int, float]],
        features: Dict[str, Union[int, float]],
        latency: float
    ) -> None:
        """예측 결과를 로깅합니다.

        Args:
            prediction: 모델의 예측값
            true_value: 실제값 (있는 경우)
            features: 입력 피처들
            latency: 예측에 걸린 시간 (초)
        """
        # Prometheus 메트릭 업데이트
        PREDICTION_COUNTER.labels(model_version=self.model_version).inc()
        PREDICTION_LATENCY.labels(model_version=self.model_version).observe(latency)

        # 예측 정보를 버퍼에 저장
        prediction_info = {
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction,
            'true_value': true_value,
            'features': features,
            'latency': latency
        }
        self.predictions_buffer.append(prediction_info)

        # 버퍼가 가득 차면 메트릭 계산 및 저장
        if len(self.predictions_buffer) >= self.buffer_size:
            self._process_buffer()

    def _process_buffer(self) -> None:
        """버퍼의 데이터를 처리하고 메트릭을 계산합니다."""
        if not self.predictions_buffer:
            return

        # 메트릭 계산
        predictions = []
        true_values = []
        latencies = []
        features_list = []

        for record in self.predictions_buffer:
            predictions.append(record['prediction'])
            if record['true_value'] is not None:
                true_values.append(record['true_value'])
            latencies.append(record['latency'])
            features_list.append(record['features'])

        # 성능 메트릭 계산 (실제값이 있는 경우)
        if true_values:
            accuracy = accuracy_score(true_values, predictions)
            precision, recall, f1, _ = precision_recall_fscore_support(
                true_values,
                predictions,
                average='weighted'
            )
            MODEL_ACCURACY.labels(model_version=self.model_version).set(accuracy)

            metrics = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'avg_latency': np.mean(latencies),
                'timestamp': datetime.now().isoformat()
            }

            # 메트릭을 파일에 저장
            self._save_metrics(metrics)

        # 데이터 드리프트 탐지 (참조 데이터가 있는 경우)
        if self.reference_data is not None:
            self._detect_data_drift(pd.DataFrame(features_list))

        # 버퍼 초기화
        self.predictions_buffer = []

    def _detect_data_drift(self, current_data: pd.DataFrame) -> None:
        """데이터 드리프트를 탐지합니다.

        Args:
            current_data: 현재 데이터
        """
        for column in current_data.columns:
            if column in self.reference_data.columns:
                # KS 테스트를 사용하여 드리프트 점수 계산
                from scipy.stats import ks_2samp
                statistic, _ = ks_2samp(
                    self.reference_data[column],
                    current_data[column]
                )
                DATA_DRIFT_SCORE.labels(feature=column).set(statistic)

    def _save_metrics(self, metrics: Dict) -> None:
        """메트릭을 파일에 저장합니다.

        Args:
            metrics: 저장할 메트릭
        """
        try:
            # 디렉토리가 없으면 생성
            self.metrics_path.parent.mkdir(parents=True, exist_ok=True)

            # 기존 메트릭이 있으면 로드
            if self.metrics_path.exists():
                with open(self.metrics_path, 'r') as f:
                    existing_metrics = json.load(f)
            else:
                existing_metrics = []

            # 새 메트릭 추가
            existing_metrics.append(metrics)

            # 파일에 저장
            with open(self.metrics_path, 'w') as f:
                json.dump(existing_metrics, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def get_metrics_summary(self) -> Dict:
        """최근 메트릭의 요약을 반환합니다."""
        try:
            with open(self.metrics_path, 'r') as f:
                metrics_history = json.load(f)
            
            if not metrics_history:
                return {}

            # 최근 100개의 메트릭만 사용
            recent_metrics = metrics_history[-100:]
            
            return {
                'accuracy': np.mean([m['accuracy'] for m in recent_metrics]),
                'precision': np.mean([m['precision'] for m in recent_metrics]),
                'recall': np.mean([m['recall'] for m in recent_metrics]),
                'f1': np.mean([m['f1'] for m in recent_metrics]),
                'avg_latency': np.mean([m['avg_latency'] for m in recent_metrics]),
                'num_predictions': len(recent_metrics)
            }

        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}

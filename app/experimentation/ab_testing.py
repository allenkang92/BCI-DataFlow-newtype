"""
A/B 테스팅을 위한 모듈입니다.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
import json
from pathlib import Path
import random
from dataclasses import dataclass

import numpy as np
from scipy import stats

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Experiment:
    """실험 설정을 위한 데이터 클래스"""
    name: str
    variant_a: str  # 컨트롤 그룹 (기존 모델)
    variant_b: str  # 실험 그룹 (새 모델)
    traffic_split: float = 0.5  # B 그룹에 할당할 트래픽 비율
    min_samples: int = 1000  # 최소 샘플 수
    confidence_level: float = 0.95  # 신뢰 수준

class ABTest:
    """A/B 테스트 실행 및 분석을 위한 클래스"""

    def __init__(
        self,
        experiment: Experiment,
        results_path: Union[str, Path]
    ):
        """
        Args:
            experiment: 실험 설정
            results_path: 결과를 저장할 경로
        """
        self.experiment = experiment
        self.results_path = Path(results_path)
        self._load_results()

    def _load_results(self) -> None:
        """저장된 실험 결과를 로드합니다."""
        try:
            if self.results_path.exists():
                with open(self.results_path, 'r') as f:
                    self.results = json.load(f)
            else:
                self.results = {
                    'variant_a': [],
                    'variant_b': []
                }
        except Exception as e:
            logger.error(f"Failed to load results: {e}")
            self.results = {
                'variant_a': [],
                'variant_b': []
            }

    def assign_variant(self, user_id: str) -> str:
        """사용자를 실험 그룹에 할당합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            할당된 변형(variant) 이름
        """
        # 결정론적 할당을 위해 user_id를 시드로 사용
        random.seed(user_id)
        if random.random() < self.experiment.traffic_split:
            return self.experiment.variant_b
        return self.experiment.variant_a

    def log_prediction(
        self,
        variant: str,
        prediction: Union[int, float],
        true_value: Union[int, float],
        metadata: Optional[Dict] = None
    ) -> None:
        """예측 결과를 기록합니다.

        Args:
            variant: 변형(variant) 이름
            prediction: 모델의 예측값
            true_value: 실제값
            metadata: 추가 메타데이터
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction,
            'true_value': true_value,
            'correct': prediction == true_value,
            'metadata': metadata or {}
        }

        if variant == self.experiment.variant_a:
            self.results['variant_a'].append(result)
        else:
            self.results['variant_b'].append(result)

        # 결과 저장
        self._save_results()

    def _save_results(self) -> None:
        """실험 결과를 파일에 저장합니다."""
        try:
            self.results_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.results_path, 'w') as f:
                json.dump(self.results, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

    def analyze_results(self) -> Dict:
        """실험 결과를 분석합니다.

        Returns:
            분석 결과를 담은 딕셔너리
        """
        # 충분한 샘플이 있는지 확인
        if (len(self.results['variant_a']) < self.experiment.min_samples or
            len(self.results['variant_b']) < self.experiment.min_samples):
            return {
                'status': 'insufficient_data',
                'message': f"Need at least {self.experiment.min_samples} samples per variant"
            }

        # 정확도 계산
        accuracy_a = np.mean([r['correct'] for r in self.results['variant_a']])
        accuracy_b = np.mean([r['correct'] for r in self.results['variant_b']])

        # 통계적 유의성 검정
        correct_a = [r['correct'] for r in self.results['variant_a']]
        correct_b = [r['correct'] for r in self.results['variant_b']]
        _, p_value = stats.ttest_ind(correct_a, correct_b)

        # 효과 크기 계산 (Cohen's d)
        pooled_std = np.sqrt(
            (np.var(correct_a) + np.var(correct_b)) / 2
        )
        effect_size = (accuracy_b - accuracy_a) / pooled_std

        # 신뢰 구간 계산
        ci_a = stats.norm.interval(
            self.experiment.confidence_level,
            loc=accuracy_a,
            scale=stats.sem(correct_a)
        )
        ci_b = stats.norm.interval(
            self.experiment.confidence_level,
            loc=accuracy_b,
            scale=stats.sem(correct_b)
        )

        return {
            'status': 'complete',
            'variant_a': {
                'accuracy': accuracy_a,
                'sample_size': len(correct_a),
                'confidence_interval': ci_a
            },
            'variant_b': {
                'accuracy': accuracy_b,
                'sample_size': len(correct_b),
                'confidence_interval': ci_b
            },
            'difference': {
                'absolute': accuracy_b - accuracy_a,
                'relative': (accuracy_b - accuracy_a) / accuracy_a * 100,
                'effect_size': effect_size
            },
            'statistical_significance': {
                'p_value': p_value,
                'significant': p_value < (1 - self.experiment.confidence_level),
                'confidence_level': self.experiment.confidence_level
            }
        }

    def get_recommendation(self) -> Dict:
        """실험 결과를 바탕으로 권장 사항을 제공합니다.

        Returns:
            권장 사항을 담은 딕셔너리
        """
        analysis = self.analyze_results()
        
        if analysis['status'] == 'insufficient_data':
            return {
                'status': 'continue',
                'message': analysis['message']
            }

        # 통계적으로 유의미한 개선이 있는 경우
        if (analysis['statistical_significance']['significant'] and
            analysis['difference']['absolute'] > 0):
            return {
                'status': 'promote_b',
                'message': (
                    f"Variant B shows significant improvement "
                    f"({analysis['difference']['relative']:.1f}% increase in accuracy)"
                ),
                'confidence_level': analysis['statistical_significance']['confidence_level']
            }

        # 통계적으로 유의미한 성능 저하가 있는 경우
        if (analysis['statistical_significance']['significant'] and
            analysis['difference']['absolute'] < 0):
            return {
                'status': 'stop',
                'message': (
                    f"Variant B shows significant degradation "
                    f"({-analysis['difference']['relative']:.1f}% decrease in accuracy)"
                ),
                'confidence_level': analysis['statistical_significance']['confidence_level']
            }

        # 충분한 데이터가 있지만 유의미한 차이가 없는 경우
        if len(self.results['variant_a']) >= self.experiment.min_samples * 2:
            return {
                'status': 'no_difference',
                'message': "No significant difference between variants",
                'confidence_level': analysis['statistical_significance']['confidence_level']
            }

        # 더 많은 데이터가 필요한 경우
        return {
            'status': 'continue',
            'message': "Continue experiment to gather more data",
            'current_samples': min(
                len(self.results['variant_a']),
                len(self.results['variant_b'])
            )
        }

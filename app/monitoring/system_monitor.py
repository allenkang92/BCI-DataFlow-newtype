"""
시스템 모니터링을 위한 모듈입니다.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Union
import json
from pathlib import Path
import psutil
import os

from prometheus_client import Counter, Gauge, Histogram, start_http_server

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus 메트릭 정의
SYSTEM_CPU_USAGE = Gauge('system_cpu_usage_percent', 'System CPU usage')
SYSTEM_MEMORY_USAGE = Gauge('system_memory_usage_bytes', 'System memory usage')
SYSTEM_DISK_USAGE = Gauge('system_disk_usage_bytes', 'System disk usage')
API_REQUEST_COUNT = Counter('api_request_total', 'Total API requests', ['endpoint', 'method', 'status'])
API_RESPONSE_TIME = Histogram(
    'api_response_time_seconds',
    'API response time',
    ['endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

class SystemMonitor:
    """시스템 리소스 모니터링을 위한 클래스"""

    def __init__(
        self,
        metrics_path: Union[str, Path],
        alert_thresholds: Optional[Dict] = None
    ):
        """
        Args:
            metrics_path: 메트릭을 저장할 경로
            alert_thresholds: 알림 임계값 설정
        """
        self.metrics_path = Path(metrics_path)
        self.alert_thresholds = alert_thresholds or {
            'cpu_percent': 80.0,
            'memory_percent': 80.0,
            'disk_percent': 80.0
        }
        self._setup_prometheus()

    def _setup_prometheus(self) -> None:
        """Prometheus 메트릭 서버를 설정합니다."""
        try:
            start_http_server(8000)
            logger.info("Started Prometheus metrics server on port 8000")
        except Exception as e:
            logger.error(f"Failed to start Prometheus server: {e}")

    def collect_metrics(self) -> Dict:
        """시스템 메트릭을 수집합니다.

        Returns:
            수집된 메트릭
        """
        try:
            # CPU 사용량
            cpu_percent = psutil.cpu_percent(interval=1)
            SYSTEM_CPU_USAGE.set(cpu_percent)

            # 메모리 사용량
            memory = psutil.virtual_memory()
            SYSTEM_MEMORY_USAGE.set(memory.used)

            # 디스크 사용량
            disk = psutil.disk_usage('/')
            SYSTEM_DISK_USAGE.set(disk.used)

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count()
                },
                'memory': {
                    'total': memory.total,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'percent': disk.percent
                },
                'network': self._get_network_stats()
            }

            self._save_metrics(metrics)
            self._check_alerts(metrics)

            return metrics

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}

    def _get_network_stats(self) -> Dict:
        """네트워크 통계를 수집합니다.

        Returns:
            네트워크 통계 정보
        """
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout
        }

    def _save_metrics(self, metrics: Dict) -> None:
        """메트릭을 파일에 저장합니다.

        Args:
            metrics: 저장할 메트릭
        """
        try:
            self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 기존 메트릭 로드
            if self.metrics_path.exists():
                with open(self.metrics_path, 'r') as f:
                    existing_metrics = json.load(f)
            else:
                existing_metrics = []

            # 새 메트릭 추가
            existing_metrics.append(metrics)

            # 최근 1000개의 메트릭만 유지
            if len(existing_metrics) > 1000:
                existing_metrics = existing_metrics[-1000:]

            # 파일에 저장
            with open(self.metrics_path, 'w') as f:
                json.dump(existing_metrics, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def _check_alerts(self, metrics: Dict) -> None:
        """메트릭을 확인하고 필요한 경우 알림을 발생시킵니다.

        Args:
            metrics: 확인할 메트릭
        """
        alerts = []

        # CPU 사용량 확인
        if metrics['cpu']['percent'] > self.alert_thresholds['cpu_percent']:
            alerts.append(
                f"High CPU usage: {metrics['cpu']['percent']}% "
                f"(threshold: {self.alert_thresholds['cpu_percent']}%)"
            )

        # 메모리 사용량 확인
        if metrics['memory']['percent'] > self.alert_thresholds['memory_percent']:
            alerts.append(
                f"High memory usage: {metrics['memory']['percent']}% "
                f"(threshold: {self.alert_thresholds['memory_percent']}%)"
            )

        # 디스크 사용량 확인
        if metrics['disk']['percent'] > self.alert_thresholds['disk_percent']:
            alerts.append(
                f"High disk usage: {metrics['disk']['percent']}% "
                f"(threshold: {self.alert_thresholds['disk_percent']}%)"
            )

        # 알림 발생
        if alerts:
            self._send_alerts(alerts)

    def _send_alerts(self, alerts: List[str]) -> None:
        """알림을 전송합니다.

        Args:
            alerts: 전송할 알림 메시지 리스트
        """
        for alert in alerts:
            logger.warning(f"ALERT: {alert}")
            # TODO: 실제 알림 전송 구현 (이메일, Slack 등)

    def get_metrics_summary(self) -> Dict:
        """최근 메트릭의 요약을 반환합니다.

        Returns:
            메트릭 요약 정보
        """
        try:
            with open(self.metrics_path, 'r') as f:
                metrics_history = json.load(f)

            if not metrics_history:
                return {}

            # 최근 100개의 메트릭 사용
            recent_metrics = metrics_history[-100:]

            return {
                'cpu': {
                    'avg_percent': sum(m['cpu']['percent'] for m in recent_metrics) / len(recent_metrics),
                    'max_percent': max(m['cpu']['percent'] for m in recent_metrics)
                },
                'memory': {
                    'avg_percent': sum(m['memory']['percent'] for m in recent_metrics) / len(recent_metrics),
                    'max_percent': max(m['memory']['percent'] for m in recent_metrics)
                },
                'disk': {
                    'avg_percent': sum(m['disk']['percent'] for m in recent_metrics) / len(recent_metrics),
                    'max_percent': max(m['disk']['percent'] for m in recent_metrics)
                },
                'time_range': {
                    'start': recent_metrics[0]['timestamp'],
                    'end': recent_metrics[-1]['timestamp']
                }
            }

        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}

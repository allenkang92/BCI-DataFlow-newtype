"""
데이터 검증을 위한 스키마 정의 모듈입니다.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
import numpy as np
import re

class EEGDataPoint(BaseModel):
    """단일 EEG 데이터 포인트를 위한 스키마"""
    
    preprocessed: str = Field(
        ...,
        description="전처리된 EEG 데이터 값들 (문자열 형식의 리스트)"
    )
    subject_id: int = Field(
        ...,
        description="피험자 ID",
        gt=0
    )
    run_id: str = Field(
        ...,
        description="실험 실행 ID"
    )
    channels: str = Field(
        ...,
        description="EEG 채널 정보"
    )
    coordsystem: str = Field(
        ...,
        description="좌표계 정보"
    )
    electrodes: str = Field(
        ...,
        description="전극 정보"
    )
    events: Optional[str] = Field(
        None,
        description="이벤트 정보 (옵션)"
    )

    @validator('preprocessed')
    def validate_preprocessed_format(cls, v):
        """전처리된 데이터 형식을 검증합니다."""
        if not re.match(r'\[[-+]?\d*\.\d+e[-+]?\d+(?:,\s*[-+]?\d*\.\d+e[-+]?\d+)*\]', v):
            raise ValueError("Invalid preprocessed data format")
        return v

    @validator('run_id')
    def validate_run_id_format(cls, v):
        """실행 ID 형식을 검증합니다."""
        if not re.match(r'^run\d+$', v):
            raise ValueError("Invalid run_id format. Should be 'runX' where X is a number")
        return v

    @validator('channels', 'electrodes')
    def validate_list_format(cls, v):
        """채널과 전극 정보 형식을 검증합니다."""
        if not re.match(r'^[a-zA-Z0-9]+(,[a-zA-Z0-9]+)*$', v):
            raise ValueError("Invalid format. Should be comma-separated values")
        return v

class EEGDataset(BaseModel):
    """전체 EEG 데이터셋을 위한 스키마"""
    
    data: List[EEGDataPoint]
    
    @validator('data')
    def validate_dataset_size(cls, v):
        """데이터셋 크기를 검증합니다."""
        if len(v) < 2:  # 최소 2개의 데이터 포인트 필요
            raise ValueError("Dataset must contain at least 2 data points")
        return v

# BCI-DataFlow-MLOps

- BCI-DataFlow-MLOps는 뇌-컴퓨터 인터페이스(BCI) 데이터 처리 및 MLOps 통합을 위한 플랫폼. 
데이터 전처리, 모델 관리, 데이터 흐름 자동화를 지원하려고 노력합니다...하하

## 프로젝트 구조

```
BCI-DataFlow-MLOps/
├── scripts/
│   ├── prepare.py
│   ├── train.py
├── static/
│   └── styles.css
├── templates/
│   ├── add_data_point.html
│   ├── base.html
│   ├── create_session.html
│   ├── dashboard.html
│   ├── delete_data_point.html
│   ├── delete_session.html
│   ├── session_detail.html
│   ├── session_list.html
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_main.py
│   ├── test_models.py
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── dvc.yaml
├── hyperparameters.yaml
├── metrics.json
├── mlflow.yaml
├── README.md
├── requirements.txt
```

### 주요 디렉토리 및 파일 설명

#### `scripts/`
- **prepare.py**: EEG 데이터셋을 전처리하는 스크립트로, 주요 필터링, 정상화, 이벤트 추출 작업을 수행
- **train.py**: 전처리된 데이터를 사용하여 머신러닝 모델을 학습시키는 스크립트

#### `static/`
- **styles.css**: 플랫폼의 UI 스타일링을 담당하는 CSS 파일

#### `templates/`
- **add_data_point.html**: 사용자가 데이터 포인트를 추가
- **base.html**: 프로젝트의 기본 HTML 레이아웃을 정의
- **create_session.html**: 새로운 세션을 생성할 수 있는 페이지
- **dashboard.html**: BCI 플랫폼의 대시보드 페이지
- **delete_data_point.html**: 데이터 포인트 삭제를 위한 페이지
- **delete_session.html**: 세션 삭제를 위한 페이지
- **session_detail.html**: 개별 세션의 세부 정보
- **session_list.html**: 세션 목록

#### `tests/`
- **test_api.py**: API 엔드포인트 테스트를 포함
- **test_main.py**: 메인 애플리케이션 로직에 대한 테스트가 포함
- **test_models.py**: 데이터베이스 모델 테스트를 포함

#### 설정 파일
- **docker-compose.yml**: Docker 컨테이너를 오케스트레이션하기 위한 설정 파일
- **Dockerfile**: 애플리케이션을 컨테이너화하기 위한 Docker 구성 파일
- **dvc.yaml**: 데이터 및 모델 버전 관리를 위해 DVC 설정 파일
- **mlflow.yaml**: MLflow 실험 관리 설정 파일
- **requirements.txt**: 프로젝트에 필요한 Python 패키지 종속성 목록을 포함

## 설치 및 실행

### 의존성 설치

이 프로젝트는 Python 3.x 및 Docker가 필요

```bash
pip install -r requirements.txt
```

Docker를 사용하여 컨테이너를 실행

```bash
docker-compose up --build
```

### MLOps 도구
- **MLflow**: 모델 실험 추적 및 관리
- **DVC**: 데이터 버전 관리
- **Airflow**: 데이터 파이프라인 자동화
- **GitHub Actions**: CI/CD 파이프라인 구축

다음은 요청하신 Auditory-Visual Shift Study 데이터셋에 대한 명세 내용을 README 파일에 통합할 수 있도록 최대한 친절하고 쉽게 설명한 예시입니다.

---

## 사용한 예시 데이터셋 설명: Auditory-Visual Shift Study

### 1. 데이터셋 개요
Auditory-Visual Shift Study는 청각 및 시각 자극에 대한 EEG(뇌전도) 데이터를 기록한 데이터셋. 연구 참가자들이 청각 또는 시각 자극에 집중하는 동안 수집된 EEG 데이터를 포함하고 있으며, 각 자극 및 반응 이벤트가 기록되어 있습니다. 여러 참가자의 여러 실행(run)으로 구성되어 있으며, 실험 중 발생한 자극과 반응 정보를 상세히 제공합니다.

### 2. 데이터 구조
데이터셋은 다음과 같이 구성되어 있습니다:
- **상위 디렉토리**: 각 참가자의 데이터를 포함한 하위 디렉토리로 구성됩니다. 예: `sub-001/`, `sub-002/` ... `sub-XXX/`
- 각 참가자 디렉토리에는 다음 파일들이 포함됩니다:
  - **EEG 데이터 파일** (`.fdt`, `.set`): EEGLAB 형식으로 저장된 뇌전도 신호 데이터.
  - **이벤트 파일** (`_events.tsv`): 실험 중 발생한 자극 및 반응 이벤트 정보를 포함한 파일.
  - **채널 파일** (`_channels.tsv`): EEG 데이터를 기록한 각 채널의 정보를 포함한 파일.
  - **전극 파일** (`_electrodes.tsv`): EEG 전극의 공간 좌표 정보.
  - **좌표 시스템 파일** (`_coordsystem.json`): 전극의 좌표 시스템 정보를 설명하는 파일.

### 3. 참가자 및 실행 정보
- **참가자 식별자**: `sub-XXX` 형식으로 구성되어 있습니다. 각 참가자는 고유한 식별자를 가지며, XXX는 참가자 번호를 의미합니다.
- **실행(run)**: 각 참가자는 동일한 실험을 여러 번 실행할 수 있으며, `run-01`, `run-02`와 같이 구분됩니다.

### 4. 각 파일의 설명

#### a. EEG 데이터 파일 (`.fdt`, `.set`)
- **확장자**: `.fdt` (이진 데이터)와 `.set` (EEGLAB 형식의 메타데이터)
- **내용**: 각 채널에서 측정된 시간에 따른 전압 변화(µV 단위).
- **샘플링 속도**: 250 Hz (초당 250 샘플).
- **채널 수**: 64개 이상의 EEG 채널과 EOG(Electrooculography) 채널이 포함될 수 있습니다.

#### b. 이벤트 파일 (`_events.tsv`)
- **내용**: 실험 중 발생한 자극 및 반응 이벤트의 시간, 이벤트 코드, 실험 조건 등을 포함한 파일.
- **주요 컬럼**:
  - `onset`: 이벤트가 발생한 시간 (초 단위).
  - `duration`: 이벤트의 지속 시간.
  - `event_type`: 이벤트의 종류 (예: 자극, 반응 등).
  - `condition`: 실험 조건에 대한 정보.
  - `event_code`, `cond_code`: 이벤트와 조건에 대한 고유 코드.

#### c. 채널 파일 (`_channels.tsv`)
- **내용**: EEG 신호를 기록한 각 채널의 정보 (채널 이름, 측정 단위, 설명 등).
- **주요 컬럼**:
  - `name`: 채널 이름 (예: Fp1, Fp2).
  - `type`: 채널의 유형 (EEG, EOG 등).
  - `units`: 측정 단위 (µV).

#### d. 전극 파일 (`_electrodes.tsv`)
- **내용**: 각 EEG 전극의 3차원 공간 좌표(CTF 좌표 시스템 기준).
- **주요 컬럼**:
  - `name`: 전극 이름.
  - `x, y, z`: 전극의 3D 좌표.

#### e. 좌표 시스템 파일 (`_coordsystem.json`)
- **내용**: EEG 전극의 좌표 시스템에 대한 설명이 포함된 JSON 파일.
- **주요 필드**:
  - `EEGCoordinateSystem`: 좌표 시스템 이름 (예: CTF).
  - `EEGCoordinateSystemDescription`: 좌표 시스템의 설명.

### 5. 전처리 단계
이 프로젝트는 EEG 데이터를 전처리하는 여러 단계를 포함하고 있습니다. 각 단계에서 데이터를 필터링하고 분석에 적합한 형식으로 변환합니다.

#### a. 파일 로드
- `.set` 파일과 관련된 `.fdt` 파일을 MNE-Python을 통해 로드하며, MATLAB v7.3 형식의 파일은 `h5py` 라이브러리를 사용하여 로드할 수 있습니다.

#### b. 채널, 전극 및 좌표 시스템 정보 로드
- `channels.tsv`, `electrodes.tsv`, `coordsystem.json` 파일을 Pandas 또는 JSON 모듈을 사용하여 로드합니다. 채널과 전극 정보는 분석에 중요한 신호의 위치를 파악하는 데 사용됩니다.

#### c. 이벤트 데이터 로드 및 동기화
- `_events.tsv` 파일을 불러와 EEG 데이터와 동기화하고, 각 이벤트 발생 시점을 샘플 단위로 변환하여 이벤트 기반 분석을 진행합니다.

#### d. 필터링 및 리샘플링
- **대역 통과 필터**: 1-50Hz 대역의 필터를 적용하여 저주파 및 고주파 잡음을 제거합니다.
- **리샘플링**: 데이터를 250Hz로 리샘플링하여 신호의 일관성을 유지합니다.

#### e. 피처 추출
- **전력 스펙트럼 밀도(PSD)**: 웰치 방법을 사용하여 각 채널에서 1-50Hz 주파수 대역의 전력 스펙트럼을 계산합니다.
- **평균 전력**: 주파수 대역의 평균값을 피처로 사용합니다.

#### f. 결과 저장
- 전처리된 EEG 데이터와 관련 정보는 CSV 및 JSON 형식으로 저장됩니다.
  - 예시: `preprocessed_sub-021_run-02_features.csv`, `channels_sub-021_run-02.csv`.

### 6. 전처리된 데이터 형식
- **피처 데이터**: 전처리된 EEG 데이터는 각 채널의 평균 전력 밀도 정보를 포함하며, CSV 형식으로 저장됩니다.
  - 파일 예시: `preprocessed_sub-XXX_run-XX_features.csv`.

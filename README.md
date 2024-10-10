# BCI-DataFlow-MLOps

BCI-DataFlow-MLOps는 뇌-컴퓨터 인터페이스(BCI) 데이터 처리 및 MLOps 통합을 위한 플랫폼입니다. 데이터 전처리, 모델 관리, 데이터 흐름 자동화를 지원하려고 노력합니다... 하하

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
- **prepare.py**: EEG 데이터셋을 전처리하는 스크립트로, 주요 필터링, 정상화, 이벤트 추출 작업을 수행합니다.
- **train.py**: 전처리된 데이터를 사용하여 머신러닝 모델을 학습시키는 스크립트입니다. MLflow를 통해 모델 실험 관리 및 로그 저장을 수행하며, DVC를 사용해 데이터와 모델을 버전 관리합니다.

#### `static/`
- **styles.css**: 플랫폼의 UI 스타일링을 담당하는 CSS 파일입니다.

#### `templates/`
- **add_data_point.html**: 사용자가 데이터 포인트를 추가할 수 있는 페이지.
- **base.html**: 프로젝트의 기본 HTML 레이아웃을 정의합니다.
- **create_session.html**: 새로운 세션을 생성할 수 있는 페이지.
- **dashboard.html**: BCI 플랫폼의 대시보드 페이지.
- **delete_data_point.html**: 데이터 포인트 삭제를 위한 페이지.
- **delete_session.html**: 세션 삭제를 위한 페이지.
- **session_detail.html**: 개별 세션의 세부 정보 페이지.
- **session_list.html**: 세션 목록을 볼 수 있는 페이지.

#### `tests/`
- **test_api.py**: API 엔드포인트에 대한 테스트가 포함되어 있습니다.
- **test_main.py**: 메인 애플리케이션 로직에 대한 테스트가 포함되어 있습니다.
- **test_models.py**: 데이터베이스 모델에 대한 테스트를 포함합니다.

#### 설정 파일
- **docker-compose.yml**: Docker 컨테이너를 오케스트레이션하기 위한 설정 파일로, 모든 서비스를 포함하여 환경을 구성합니다 (예: 웹 서비스, MLflow, 데이터 저장소 등).
- **Dockerfile**: 애플리케이션을 컨테이너화하기 위한 Docker 구성 파일로, 필요한 모든 패키지와 설정이 포함되어 있습니다.
- **dvc.yaml**: 데이터 및 모델 버전 관리를 위해 DVC 설정 파일이 작성되어 있으며, 각 스테이지는 전처리, 학습, 평가로 구성되어 있습니다.
- **mlflow.yaml**: MLflow 실험 관리 및 결과를 저장하는 설정 파일입니다.
- **requirements.txt**: 프로젝트에 필요한 Python 패키지 종속성 목록을 포함하며, 이를 설치하여 환경을 구축할 수 있습니다.

## 설치 및 실행

### 의존성 설치

이 프로젝트는 Python 3.x 및 Docker가 필요합니다.

```bash
pip install -r requirements.txt
```

Docker를 사용하여 컨테이너를 실행할 수 있습니다.

```bash
docker-compose up --build
```

## 데이터셋 설명: Auditory-Visual Shift Study
[https://openneuro.org/datasets/ds002893/versions/2.0.0](https://openneuro.org/datasets/ds002893/versions/2.0.0)

이 데이터셋은 청각 및 시각 자극에 대한 EEG 데이터를 포함하고 있으며, 각각의 이벤트와 반응을 기록한 정보가 포함되어 있습니다. 전처리된 데이터는 각 참가자의 여러 실행(run)으로 구분되며, 자극과 반응이 기록된 타임스탬프와 함께 제공됩니다.

### 데이터 구조
- EEG 데이터는 `.set` 및 `.fdt` 파일로 저장되며, 각 실행에 대한 이벤트는 `_events.tsv` 파일에 기록됩니다.
- EEG 채널 정보는 `_channels.tsv`, 전극 좌표는 `_electrodes.tsv`, 좌표 시스템 정보는 `_coordsystem.json`에 저장됩니다.

### 전처리 단계
- EEG 데이터를 필터링 및 리샘플링한 후, 전력 스펙트럼 밀도(PSD)를 계산하고, 주파수 대역의 평균 전력을 피처로 사용합니다.
- 전처리된 데이터는 CSV 파일 형식으로 저장되며, 각 실험의 피처를 포함합니다.

```bash
dvc repro  # DVC 파이프라인 재실행
```

## MLflow 통합
이 프로젝트는 MLflow를 사용하여 모델 학습 실험을 기록합니다. 학습 중 기록된 메트릭과 하이퍼파라미터, 모델 자체는 MLflow를 통해 관리됩니다.

```bash
# MLflow UI 실행
docker-compose exec mlflow mlflow ui
```

## Docker 환경 구성
- **Docker Compose**를 사용하여 모든 스크립트 및 실행 환경이 컨테이너 내에서 동작하도록 설정되었습니다.
- **MLflow** 서버, **SQLite** 데이터베이스, 데이터 처리 및 학습 스크립트가 모두 컨테이너 내에서 실행됩니다.

## DVC 통합
DVC를 통해 데이터셋과 모델의 버전 관리가 이루어집니다. 전처리 단계 및 학습, 평가 단계를 DVC 스테이지로 관리하며, 데이터 및 모델 변경 사항을 추적할 수 있습니다.


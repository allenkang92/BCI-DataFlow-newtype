# 베이스 이미지로 Python 3.9 사용
FROM python:3.9

# 작업 디렉토리 설정
WORKDIR /code

# requirements.txt 복사 및 존재 여부 확인
COPY ./requirements.txt /code/requirements.txt
RUN ls -al /code && cat /code/requirements.txt  # 파일 확인을 위한 디버깅 명령어 추가

# pip 설치 전에 pip 최신 버전으로 업데이트 (권장)
RUN pip install --upgrade pip

# requirements.txt에 명시된 패키지 설치
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# MLflow 설치 추가
RUN pip install mlflow

# 코드, 환경설정, static 파일 복사
COPY ./app /code/app
COPY ./.env /code/.env
COPY ./static /code/static

# MLflow 트래킹 URI 설정
ENV MLFLOW_TRACKING_URI=http://mlflow:5000

# FastAPI 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

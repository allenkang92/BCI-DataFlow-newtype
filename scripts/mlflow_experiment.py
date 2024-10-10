import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder
import mlflow
import mlflow.sklearn

# 데이터 파일 경로 설정
data_path = '/code/data/processed/eeg_data.csv'

# 데이터 로드
data = pd.read_csv(data_path)

# 'preprocessed' 컬럼 처리
def process_preprocessed(x):
    values = x.split('\n')[1:]  # 첫 번째 줄 제거
    return [float(v.split()[1]) for v in values]  # 두 번째 열의 값만 추출

data['preprocessed'] = data['preprocessed'].apply(process_preprocessed)
preprocessed_df = pd.DataFrame(data['preprocessed'].tolist())
preprocessed_df.columns = [f'feature_{i}' for i in range(preprocessed_df.shape[1])]

# 데이터 병합 - 필요없는 컬럼 제거
data = pd.concat([data[['subject_id', 'run_id']], preprocessed_df], axis=1)

# 범주형 변수 인코딩
le = LabelEncoder()
data['subject_id'] = le.fit_transform(data['subject_id'])

# 특성과 타겟 분리
X = data.drop(columns=['subject_id', 'run_id'])
y = data['subject_id']

# 클래스 분포 확인
print("클래스 분포:", np.bincount(y))

# MLflow 실험 시작
mlflow.set_experiment("BCI-DataFlow-Experiment")

with mlflow.start_run():
    # 모델 학습
    rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    rf.fit(X, y)
    
    # 예측
    y_pred = rf.predict(X)
    
    # 평가 메트릭 계산
    accuracy = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred, average='weighted')
    precision = precision_score(y, y_pred, average='weighted')
    recall = recall_score(y, y_pred, average='weighted')
    
    # MLflow에 로깅
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    
    # 모델 저장
    mlflow.sklearn.log_model(rf, "random_forest_model")

print("실험이 완료되었습니다. MLflow에서 기록된 결과를 확인하세요.")
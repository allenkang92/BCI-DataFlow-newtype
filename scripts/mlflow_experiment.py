import mlflow
import mlflow.sklearn
import pandas as pd
import re
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 데이터 경로 설정 (컨테이너 내부 경로)
data_path = "/code/data/processed/eeg_data.csv"

# 데이터 로드
data = pd.read_csv(data_path)

# 컬럼 목록 확인
print("Loaded data columns:", data.columns)

# 타겟 변수 'preprocessed'의 고유 값 출력
print("Unique values in 'preprocessed':", data["preprocessed"].unique())

# 함수 정의: 문자열에서 숫자 추출
def extract_numbers(s):
    return [float(num) for num in re.findall(r"[-+]?\d*\.\d+e[-+]?\d+", s)]

# 'preprocessed' 컬럼에서 숫자 추출하여 새로운 컬럼으로 저장
data["preprocessed_values"] = data["preprocessed"].apply(extract_numbers)

# 리스트 형태의 데이터를 각 열로 분할
preprocessed_df = pd.DataFrame(data["preprocessed_values"].tolist())

# 필요한 경우, 열 이름을 지정 (예: 'feature_0', 'feature_1', ...)
preprocessed_df.columns = [f'feature_{i}' for i in range(preprocessed_df.shape[1])]

# 데이터 병합
data = pd.concat([data.drop(columns=["preprocessed", "preprocessed_values"]), preprocessed_df], axis=1)

# NaN이 있는 행 제거
data.dropna(inplace=True)

# 타겟 변수 설정 (예시로 'subject_id'를 사용)
y = data["subject_id"]  # 예측하려는 타겟 변수로 변경

# 특성 변수 설정
X = data.drop(columns=["subject_id", "run_id", "channels", "coordsystem", "electrodes", "events"], errors='ignore')

# X와 y가 비어있는지 체크
if X.empty or y.empty:
    print("X shape:", X.shape)
    print("y shape:", y.shape)
    raise ValueError("Input data (X) or target variable (y) is empty after cleaning.")

# 학습 데이터와 테스트 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# MLflow 실험 시작
mlflow.set_experiment("BCI-DataFlow-Experiment")

with mlflow.start_run():
    # 모델 정의 및 학습
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # 예측 및 평가
    accuracy = clf.score(X_test, y_test)

    # 파라미터와 메트릭 기록
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", accuracy)

    # 모델 저장
    mlflow.sklearn.log_model(clf, "random_forest_model")

print("실험이 완료되었습니다. MLflow에서 기록된 결과를 확인하세요.")

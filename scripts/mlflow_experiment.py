import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 데이터 경로 설정 (컨테이너 내부 경로)
data_path = "/code/data/processed/eeg_data.csv"

# 데이터 로드
data = pd.read_csv(data_path)

# 컬럼 목록 확인
print("Loaded data columns:", data.columns)

# 비수치형 데이터를 제외하고 수치형 데이터만 추출
# 'preprocessed'는 타겟 변수로 설정
X = data.drop(columns=["subject_id", "run_id", "channels", "coordsystem", "electrodes", "events"], errors='ignore')
y = data["preprocessed"]

# X, y가 비어있는지 체크
if X.empty or y.empty:
    raise ValueError("Input data (X) or target variable (y) is empty.")

# y가 수치형인지 확인
if not pd.api.types.is_numeric_dtype(y):
    print("Target variable 'preprocessed' is not numeric. Attempting to convert.")
    try:
        # 숫자로 변환, 실패하면 NaN 처리
        y = pd.to_numeric(y, errors='coerce')  
    except Exception as e:
        raise ValueError(f"Could not convert target variable to numeric: {e}")

# NaN이 있는 인덱스 제거
valid_indices = y.dropna().index
X = X.loc[valid_indices]
y = y.dropna()

# X, y가 비어있지 않은지 다시 체크
if X.empty or y.empty:
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

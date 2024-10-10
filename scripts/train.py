import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import mlflow
import mlflow.sklearn
import yaml
import os
import re

def train_model(data_path, model_output_path, hyperparameters_path):
    print(f"Loading data from {data_path}")
    # Load data
    data = pd.read_csv(data_path)
    
    print(f"Data shape: {data.shape}")
    
    # 'preprocessed_values'에서 숫자형 데이터를 추출하여 각 열로 분리
    def extract_numbers(s):
        return [float(num) for num in re.findall(r"[-+]?\d*\.\d+e[-+]?\d+", s)]
    
    data["preprocessed_values"] = data["preprocessed"].apply(extract_numbers)
    preprocessed_df = pd.DataFrame(data["preprocessed_values"].tolist())
    preprocessed_df.columns = [f'feature_{i}' for i in range(preprocessed_df.shape[1])]

    # 기존 데이터와 숫자형 데이터 병합
    data = pd.concat([data.drop(columns=["preprocessed", "preprocessed_values"]), preprocessed_df], axis=1)

    print(f"Expanded data shape: {data.shape}")
    
    # 특성 데이터(X)와 타겟 데이터(y) 설정 (예시로 'subject_id' 사용)
    X = data.drop(columns=["subject_id", "run_id", "channels", "coordsystem", "electrodes", "events"], errors='ignore')
    y = data["subject_id"]  # 예시 타겟 변수

    print("Loading hyperparameters")
    # Load hyperparameters
    with open(hyperparameters_path, 'r') as file:
        hyperparameters = yaml.safe_load(file)

    print("Starting model training")
    # Train model
    with mlflow.start_run():
        mlflow.log_params(hyperparameters)
        
        model = RandomForestClassifier(**hyperparameters)
        model.fit(X, y)

        print("Logging model")
        # Log model
        mlflow.sklearn.log_model(model, "model")

        # 모델을 저장할 디렉터리가 없으면 생성
        model_dir = os.path.dirname(model_output_path)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        print(f"Saving model to {model_output_path}")
        # Save model
        joblib.dump(model, model_output_path)

        # Evaluate model
        accuracy = model.score(X, y)
        
        print(f"Model accuracy: {accuracy}")
        mlflow.log_metric("accuracy", accuracy)

    print(f"Model training complete. Model saved to {model_output_path}")

if __name__ == "__main__":
    data_path = '/code/data/processed/eeg_data.csv'
    model_output_path = '/code/models/model.pkl'
    hyperparameters_path = '/code/hyperparameters.yaml'  # 수정된 경로
    
    print(f"Checking if data file exists: {os.path.exists(data_path)}")
    print(f"Current working directory: {os.getcwd()}")
    
    train_model(data_path, model_output_path, hyperparameters_path)

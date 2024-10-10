import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import json

def evaluate_model(model_path, test_data_path):
    # Load model
    model = joblib.load(model_path)

    # Load test data
    test_data = pd.read_csv(test_data_path)
    X_test = test_data.drop('target', axis=1)
    y_test = test_data['target']

    # Make predictions
    y_pred = model.predict(X_test)

    # Calculate metrics
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average='weighted'),
        "recall": recall_score(y_test, y_pred, average='weighted'),
        "f1": f1_score(y_test, y_pred, average='weighted')
    }

    # Log metrics with MLflow
    with mlflow.start_run():
        mlflow.log_metrics(metrics)

    # Save metrics
    with open('metrics.json', 'w') as f:
        json.dump(metrics, f)

    print("Evaluation complete. Metrics saved to metrics.json")

if __name__ == "__main__":
    evaluate_model('models/model.pkl', 'data/processed/test_data.csv')
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import mlflow
import yaml

def train_model(train_data_path, model_output_path):
    # Load training data
    train_data = pd.read_csv(train_data_path)
    X_train = train_data.drop('target', axis=1)
    y_train = train_data['target']

    # Load hyperparameters
    with open('hyperparameters.yaml', 'r') as file:
        hyperparameters = yaml.safe_load(file)

    # Train model
    with mlflow.start_run():
        mlflow.log_params(hyperparameters)
        
        model = RandomForestClassifier(**hyperparameters)
        model.fit(X_train, y_train)

        # Log model
        mlflow.sklearn.log_model(model, "model")

        # Save model
        joblib.dump(model, model_output_path)

    print(f"Model training complete. Model saved to {model_output_path}")

if __name__ == "__main__":
    train_model('data/processed/train_data.csv', 'models/model.pkl')
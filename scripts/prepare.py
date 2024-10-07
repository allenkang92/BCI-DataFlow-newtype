import pandas as pd
from sklearn.model_selection import train_test_split

def prepare_data(input_file, output_train, output_test):
    # Load data
    data = pd.read_csv(input_file)

    # Perform any necessary preprocessing
    # For example, handling missing values, encoding categorical variables, etc.

    # Split data into train and test sets
    train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

    # Save processed data
    train_data.to_csv(output_train, index=False)
    test_data.to_csv(output_test, index=False)

    print(f"Data preparation complete. Train data saved to {output_train}, test data saved to {output_test}")

if __name__ == "__main__":
    prepare_data('data/raw/raw_data.csv', 'data/processed/train_data.csv', 'data/processed/test_data.csv')
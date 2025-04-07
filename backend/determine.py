import os
import pickle
import pandas as pd
import lightgbm as lgb
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# Load the preprocessor and best model
base_dir = os.path.dirname(os.path.abspath(__file__))
preprocessor_file = os.path.join(base_dir, 'preprocessor.pkl')
best_model_file = os.path.join(base_dir, 'best_model.pkl')

with open(preprocessor_file, 'rb') as f:
    preprocessor = pickle.load(f)

# Load the LightGBM model with pickle
with open(best_model_file, 'rb') as f:
    best_model = pickle.load(f)

# Load the new data for prediction
input_file = os.path.join(base_dir, '..\\files\\dummy_network_data.csv')  # Use the dummy data file
df = pd.read_csv(input_file)

# Generate missing features (similar to the training code)
if 'Time' in df.columns:
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')  # Convert Time to datetime
    df['duration'] = df['Time'].diff().fillna(pd.Timedelta(seconds=0))  # Calculate duration as the difference in time
    df['duration'] = df['duration'].dt.total_seconds()  # Convert timedelta to seconds
if 'Length' in df.columns:
    df['src_bytes'] = df['Length']
    df['dst_bytes'] = df['Length']  # Assuming Length is the total packet size for simplicity

# Handle missing categorical columns
categorical_columns = ['protocol_type', 'service', 'flag']

for col in categorical_columns:
    if col not in df.columns:
        # If the column is missing, fill it with a placeholder value
        df[col] = 'unknown'

# Ensure required columns are present
required_columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'label']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    print(f"Missing columns: {missing_columns}")
else:
    # Prepare the features dataframe (exclude 'label' for prediction)
    X = df.drop('label', axis=1, errors='ignore')

    # Transform features using the preprocessor
    X_transformed = preprocessor.transform(X)

    # Predict probabilities using the LightGBM model
    y_prob = best_model.predict(X_transformed)

    # Convert probabilities into predicted labels
    y_pred = [1 if prob > 0.5 else 0 for prob in y_prob]  # Assuming binary classification (malicious=1, normal=0)

    # Output the predictions and probabilities
    print("Predictions (with probabilities):")
    for idx, (pred, prob) in enumerate(zip(y_pred, y_prob)):
        label = "Malicious" if pred == 1 else "Normal"
        print(f"Row {idx+1}: Predicted label: {label}, Probability: {prob}")

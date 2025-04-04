import os
import pandas as pd
import pickle
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# Define the same Wireshark-exportable features (without label, since prediction input does not have it)
wireshark_features = [
    'duration', 
    'protocol_type', 
    'service', 
    'flag', 
    'src_bytes', 
    'dst_bytes', 
    'land', 
    'wrong_fragment', 
    'urgent'
]

# Define categorical and numerical features as used in training
categorical_features = ['protocol_type', 'service', 'flag']
numerical_features = [col for col in wireshark_features if col not in categorical_features]

# Path for the preprocessor and model files in the same directory as this script
base_dir = os.path.dirname(os.path.abspath(__file__))
preprocessor_file = os.path.join(base_dir, 'preprocessor.pkl')
best_model_file = os.path.join(base_dir, 'best_model.pkl')  # Corrected file name

# Load the cleaned data (processed by clean_data.py)
input_file = os.path.join(base_dir, '../files/normalized_data.csv')
df = pd.read_csv(input_file)

# Prepare the features dataframe (ensure columns are in the correct order)
# For prediction, we use the wireshark_features columns
X = df[wireshark_features]

# Load or fit the preprocessor used during model training
if os.path.exists(preprocessor_file):
    with open(preprocessor_file, 'rb') as f:
        preprocessor = pickle.load(f)
else:
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ]
    )
    preprocessor.fit(X)
    with open(preprocessor_file, 'wb') as f:
        pickle.dump(preprocessor, f)
        
# Transform the features
X_transformed = preprocessor.transform(X)

# Load the best model; if best_model.pkl doesn't exist, default to catboost_model.pkl
if not os.path.exists(best_model_file):
    default_model_file = os.path.join(base_dir, 'catboost_model.pkl')
    print("Best model file not found. Defaulting to CatBoost model.")
    best_model_file = default_model_file

with open(best_model_file, 'rb') as f:
    model = pickle.load(f)

# Predict using the loaded model
predictions = model.predict(X_transformed)

# Output the predictions
print("Predictions for the uploaded data:")
for idx, pred in enumerate(predictions):
    label = "Malicious" if pred == 1 else "Normal"
    print(f"Row {idx+1}: {label}")

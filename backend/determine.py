import os
import pickle
import pandas as pd
import numpy as np
import json
import shap
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# Load the preprocessor and best model
base_dir = os.path.dirname(os.path.abspath(__file__))
preprocessor_file = os.path.join(base_dir, 'preprocessor.pkl')
best_model_file = os.path.join(base_dir, 'best_model.pkl')

with open(preprocessor_file, 'rb') as f:
    preprocessor = pickle.load(f)

with open(best_model_file, 'rb') as f:
    best_model = pickle.load(f)

# Load the new data for prediction
input_file = os.path.join(base_dir, '../files/normalized_data.csv')
df = pd.read_csv(input_file)

# Prepare the features dataframe (exclude 'label' for prediction)
X = df.drop('label', axis=1, errors='ignore')

# Transform features using the preprocessor
X_transformed = preprocessor.transform(X)

# Predict probabilities and labels
y_prob = best_model.predict_proba(X_transformed)[:, 1]  # Probability of class 1 (malicious)
y_pred = (y_prob >= 0.5).astype(int)

# Get feature names from preprocessor
feature_names = preprocessor.get_feature_names_out()

# Initialize SHAP explainer for CatBoost
explainer = shap.TreeExplainer(best_model)

# Collect malicious rows with reasons
malicious_indices = np.where(y_pred == 1)[0]
malicious_rows = []
for idx in malicious_indices:
    # Compute SHAP values for the current sample
    shap_values = explainer.shap_values(X_transformed[idx:idx+1])  # SHAP values for the positive class (malicious)
    contributions = shap_values[0]  # Contributions for the single sample
    top_indices = np.argsort(-np.abs(contributions))[:3]  # Top 3 contributing features by absolute contribution
    reasons = []
    for feat_idx in top_indices:
        feat_name = feature_names[feat_idx]
        if feat_name.startswith('num__'):
            original_feat = feat_name[5:]
            value = df.iloc[idx][original_feat]
            reasons.append(f"{original_feat}: {value}")
        elif feat_name.startswith('cat__'):
            parts = feat_name[5:].split('_', 1)
            original_feat = parts[0]
            category = parts[1]
            reasons.append(f"{original_feat}: {category}")
    # Extract source IP if available, otherwise use a placeholder
    source_ip = df.iloc[idx]['Source'] if 'Source' in df.columns else 'Unknown'
    malicious_rows.append({
        'row_index': int(idx),
        'prediction': 'Malicious',
        'probability': float(y_prob[idx]),
        'reasons': reasons,
        'source_ip': source_ip
    })

# Prepare results dictionary
results = {
    'total_packets': len(df),
    'normal': len(df) - len(malicious_indices),
    'malicious': len(malicious_indices),
    'malicious_rows': malicious_rows
}

# Save results to JSON
output_file = os.path.join(base_dir, '../files/analysis_results.json')
with open(output_file, 'w') as f:
    json.dump(results, f)
import os
import pickle
import pandas as pd
import numpy as np
import json
import shap
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

class NetworkAnalyzer:
    def __init__(self, input_file, output_file, preprocessor_file, best_model_file):
        self.input_file = input_file
        self.output_file = output_file
        self.preprocessor_file = preprocessor_file
        self.best_model_file = best_model_file
        self.preprocessor = None
        self.best_model = None
        self.df = None

    def load_models(self):
        with open(self.preprocessor_file, 'rb') as f:
            self.preprocessor = pickle.load(f)

        with open(self.best_model_file, 'rb') as f:
            self.best_model = pickle.load(f)

    def analyze(self):
        self.df = pd.read_csv(self.input_file)

        X = self.df.drop('label', axis=1, errors='ignore')
        X_transformed = self.preprocessor.transform(X)

        y_prob = self.best_model.predict_proba(X_transformed)[:, 1]
        y_pred = (y_prob >= 0.5).astype(int)

        feature_names = self.preprocessor.get_feature_names_out()
        explainer = shap.TreeExplainer(self.best_model)

        malicious_indices = np.where(y_pred == 1)[0]
        malicious_rows = []
        for idx in malicious_indices:
            shap_values = explainer.shap_values(X_transformed[idx:idx+1])
            contributions = shap_values[0]
            top_indices = np.argsort(-np.abs(contributions))[:3]
            reasons = []
            for feat_idx in top_indices:
                feat_name = feature_names[feat_idx]
                if feat_name.startswith('num__'):
                    original_feat = feat_name[5:]
                    value = self.df.iloc[idx][original_feat]
                    reasons.append(f"{original_feat}: {value}")
                elif feat_name.startswith('cat__'):
                    parts = feat_name[5:].split('_', 1)
                    original_feat = parts[0]
                    category = parts[1]
                    reasons.append(f"{original_feat}: {category}")
            source_ip = self.df.iloc[idx]['Source'] if 'Source' in self.df.columns else 'Unknown'
            malicious_rows.append({
                'row_index': int(idx),
                'prediction': 'Malicious',
                'probability': float(y_prob[idx]),
                'reasons': reasons,
                'source_ip': source_ip
            })

        results = {
            'total_packets': len(self.df),
            'normal': len(self.df) - len(malicious_indices),
            'malicious': len(malicious_indices),
            'malicious_rows': malicious_rows
        }

        with open(self.output_file, 'w') as f:
            json.dump(results, f)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    preprocessor_file = os.path.join(base_dir, 'preprocessor.pkl')
    best_model_file = os.path.join(base_dir, 'best_model.pkl')
    input_file = os.path.join(base_dir, '../files/normalized_data.csv')
    output_file = os.path.join(base_dir, '../files/analysis_results.json')

    analyzer = NetworkAnalyzer(input_file, output_file, preprocessor_file, best_model_file)
    analyzer.load_models()
    analyzer.analyze()
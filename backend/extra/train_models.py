# Install required packages (if not already installed)
# %pip install catboost
# %pip install scikit-learn
# %pip install lightgbm
# %pip install pytorch-tabnet

import kagglehub
import pandas as pd
import numpy as np
import os
import pickle
import torch
import lightgbm as lgb

from catboost import CatBoostClassifier
from pytorch_tabnet.tab_model import TabNetClassifier

from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

# Download latest version of dataset from KaggleHub
path = kagglehub.dataset_download("hassan06/nslkdd")
print("Path to dataset files:", path)

# Define file paths for training and testing
train_file_path = os.path.join(path, 'versions/1/KDDTrain+.txt')
test_file_path = os.path.join(path, 'versions/1/KDDTest+.txt')

# Define full column names (from NSL-KDD)
column_names = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
    'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
    'num_compromised', 'root_shell', 'su_attempted', 'num_root',
    'num_file_creations', 'num_shells', 'num_access_files', 'num_outbound_cmds',
    'is_host_login', 'is_guest_login', 'count', 'srv_count', 'serror_rate',
    'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate',
    'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
    'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label', 'difficulty'
]

# Define Wireshark-exportable features only
wireshark_features = [
    'duration', 
    'protocol_type', 
    'service', 
    'flag', 
    'src_bytes', 
    'dst_bytes', 
    'land', 
    'wrong_fragment', 
    'urgent', 
    'label'
]

# Load the datasets with proper column names
df_train = pd.read_csv(train_file_path, names=column_names, index_col=False)
df_test  = pd.read_csv(test_file_path, names=column_names, index_col=False)

# Retain only the Wireshark-exportable features
df_train = df_train[wireshark_features]
df_test  = df_test[wireshark_features]

# For consistency in classification, assume that label is a string
# Convert label: 'normal' -> 0 and any attack label -> 1
def convert_label(x):
    return 0 if str(x).strip().lower() == 'normal' else 1

df_train['label'] = df_train['label'].apply(convert_label)
df_test['label']  = df_test['label'].apply(convert_label)

# Identify categorical and numerical features
categorical_features = ['protocol_type', 'service', 'flag']
numerical_features = [col for col in wireshark_features if col not in categorical_features + ['label']]

# Prepare combined data for consistent encoding
df_combined = pd.concat([df_train, df_test], ignore_index=True)

# Define the preprocessor for categorical and numerical columns
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
        ('num', StandardScaler(), numerical_features)
    ]
)

# Prepare features and labels from combined dataset
X_combined = df_combined.drop('label', axis=1)
y_combined = df_combined['label']

# Split back into training and testing sets based on original sizes
X_train = X_combined.iloc[:len(df_train), :]
X_test  = X_combined.iloc[len(df_train):, :]
y_train = y_combined.iloc[:len(df_train)]
y_test  = y_combined.iloc[len(df_train):]

# Fit and transform features using the preprocessor
X_train = preprocessor.fit_transform(X_train)
X_test  = preprocessor.transform(X_test)

############################################
# Train and evaluate CatBoost model
############################################
catboost_model = CatBoostClassifier(iterations=1000, learning_rate=0.1, depth=6, verbose=200)
catboost_model.fit(X_train, y_train, eval_set=(X_test, y_test), early_stopping_rounds=10)

# Evaluate CatBoost
y_pred_cat = catboost_model.predict(X_test)
cat_accuracy  = accuracy_score(y_test, y_pred_cat)
cat_precision = precision_score(y_test, y_pred_cat)
cat_recall    = recall_score(y_test, y_pred_cat)
cat_f1        = f1_score(y_test, y_pred_cat)

print("CatBoost Metrics:")
print(f"  Accuracy: {cat_accuracy:.2f}")
print(f"  Precision: {cat_precision:.2f}")
print(f"  Recall: {cat_recall:.2f}")
print(f"  F1 Score: {cat_f1:.2f}")

############################################
# Train and evaluate LightGBM model
############################################
# For LightGBM, create Dataset objects
train_data = lgb.Dataset(X_train, label=y_train)
valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

lgb_params = {
    'objective': 'binary',
    'metric': 'binary_error',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.1,
    'feature_fraction': 0.9,
    'verbose': -1
}

lgb_model = lgb.train(
    lgb_params,
    train_data,
    num_boost_round=1000,
    valid_sets=[valid_data],
    early_stopping_rounds=10,
    verbose_eval=100
)

# LightGBM predictions: returns probabilities; convert to binary with threshold 0.5
preds_lgb_prob = lgb_model.predict(X_test)
y_pred_lgb = (preds_lgb_prob >= 0.5).astype(int)

lgb_accuracy  = accuracy_score(y_test, y_pred_lgb)
lgb_precision = precision_score(y_test, y_pred_lgb)
lgb_recall    = recall_score(y_test, y_pred_lgb)
lgb_f1        = f1_score(y_test, y_pred_lgb)

print("\nLightGBM Metrics:")
print(f"  Accuracy: {lgb_accuracy:.2f}")
print(f"  Precision: {lgb_precision:.2f}")
print(f"  Recall: {lgb_recall:.2f}")
print(f"  F1 Score: {lgb_f1:.2f}")

############################################
# Train and evaluate TabNet model
############################################
# TabNet works directly with numpy arrays
tabnet_model = TabNetClassifier(
    n_d=8,
    n_a=8,
    n_steps=3,
    gamma=1.3,
    lambda_sparse=1e-5,
    clip_value=2.0,
    optimizer_fn=torch.optim.Adam,
    optimizer_params=dict(lr=2e-2),
    mask_type="entmax"  # "sparsemax" also works
)

# Fit TabNet (note: TabNet expects labels as a numpy array of shape (n_samples,))
tabnet_model.fit(
    X_train, y_train.values,
    eval_set=[(X_test, y_test.values)],
    max_epochs=100,
    patience=10,
    batch_size=1024,
    virtual_batch_size=128,
    num_workers=0,
    drop_last=False
)

y_pred_tabnet = tabnet_model.predict(X_test)
tabnet_accuracy  = accuracy_score(y_test, y_pred_tabnet)
tabnet_precision = precision_score(y_test, y_pred_tabnet)
tabnet_recall    = recall_score(y_test, y_pred_tabnet)
tabnet_f1        = f1_score(y_test, y_pred_tabnet)

print("\nTabNet Metrics:")
print(f"  Accuracy: {tabnet_accuracy:.2f}")
print(f"  Precision: {tabnet_precision:.2f}")
print(f"  Recall: {tabnet_recall:.2f}")
print(f"  F1 Score: {tabnet_f1:.2f}")

############################################
# Compare the models based on F1 Score and save the best model
############################################
model_metrics = {
    "CatBoost": cat_f1,
    "LightGBM": lgb_f1,
    "TabNet": tabnet_f1
}

best_model_name = max(model_metrics, key=model_metrics.get)
print("\n-------------------------")
print("Model Comparison (Based on F1 Score):")
for model_name, f1 in model_metrics.items():
    print(f"  {model_name}: F1 Score = {f1:.2f}")

print(f"\nMost Efficient Model: {best_model_name} (Highest F1 Score)")

# Determine which model object is best
if best_model_name == "CatBoost":
    best_model_obj = catboost_model
elif best_model_name == "LightGBM":
    best_model_obj = lgb_model
elif best_model_name == "TabNet":
    best_model_obj = tabnet_model

# Save the best model as best_model.pkl in the same directory as this script
best_model_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'best_model.pkl')
with open(best_model_filename, 'wb') as f:
    pickle.dump(best_model_obj, f)
print(f"Best model saved as {best_model_filename}")

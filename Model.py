import pandas as pd
import os
from pytorch_tabnet.tab_model import TabNetClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load csv file already normalized

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files/normalized_data.csv')

df = pd.read_csv(file_path)

# Training model on the basis of Protocol used
X = df.drop('Protocol', axis=1).values  # Features
y = df['Malicious'].values  # Target


# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalize the data (optional but recommended for TabNet)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Define and train the TabNet model
model = TabNetClassifier()
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], max_epochs=100, patience=10, batch_size=1024, virtual_batch_size=128)

# Make predictions
predictions = model.predict(X_test)

# Evaluate model (accuracy)
from sklearn.metrics import accuracy_score
print(f'Accuracy: {accuracy_score(y_test, predictions)}')



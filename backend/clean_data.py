import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os

# Define file paths
input_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/network_data.csv')
output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/normalized_data.csv')

# Load CSV data exported from Wireshark
def load_data(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    df = pd.read_csv(input_file)

    # Drop unnecessary columns if any (modify based on dataset structure)
    df = df.drop(columns=['No.', 'Info'], errors='ignore')

    # Encode categorical variables (e.g., Protocol)
    if 'Protocol' in df.columns:
        encoder = LabelEncoder()
        df['Protocol'] = encoder.fit_transform(df['Protocol'])

    # Normalize numerical features
    numeric_cols = ['Length', 'Time']
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save processed data to CSV
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

# Run data processing
load_data(input_file, output_file)

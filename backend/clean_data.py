import pandas as pd
import os

# Define the Wireshark-exportable features (for prediction, we exclude the label column)
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

def drop_columns(input_file, output_file, allowed_cols):
    """Retains only allowed columns from the dataset and drops rows with missing values."""
    df = pd.read_csv(input_file)
    
    # Keep only allowed columns that exist in the dataset
    df = df[[col for col in allowed_cols if col in df.columns]]
    
    # Drop rows with any missing values
    df.dropna(inplace=True)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Data cleaned and saved to {output_file}")

if __name__ == "__main__":
    input_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/network_data.csv')
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/normalized_data.csv')
    
    drop_columns(input_file, output_file, wireshark_features)

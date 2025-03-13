import pandas as pd
import os

# Define file paths
input_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/network_data.csv')
output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/normalized_data.csv')

def load_data(input_file, output_file):
    # Read the original CSV file
    df = pd.read_csv(input_file)

    # Drop columns we don't need (if they exist)
    drop_cols = ['No.', 'Info']
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

    # Preserve the original column order (minus any dropped columns)
    original_columns = df.columns.tolist()

    # No scaling or encoding is done here:
    # - We keep Protocol as text
    # - We keep Time and Length as they are in the original data

    # Reorder columns to match the original (after dropping)
    df = df[original_columns]

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save the processed data to CSV without the index
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

# Run data processing
load_data(input_file, output_file)

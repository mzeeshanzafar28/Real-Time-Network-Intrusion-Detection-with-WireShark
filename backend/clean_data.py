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
    'urgent',
    'label' 
]

def generate_missing_columns(df):
    """Generate missing columns based on available information."""
    
    # Generate 'duration' if 'Time' column exists
    if 'Time' in df.columns:
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')  # Convert Time to datetime
        df['duration'] = df['Time'].diff().fillna(pd.Timedelta(seconds=0))  # Calculate duration as the difference in time
        df['duration'] = df['duration'].dt.total_seconds()  # Convert timedelta to seconds
    
    # Generate 'src_bytes' and 'dst_bytes' from 'Length' if available, otherwise use placeholder
    if 'Length' in df.columns:
        df['src_bytes'] = df['Length']
        df['dst_bytes'] = df['Length']  # Assuming Length is the total packet size for simplicity
    else:
        df['src_bytes'] = 0  # Placeholder if 'Length' is missing
        df['dst_bytes'] = 0  # Placeholder if 'Length' is missing

    # Add missing columns with default values if they are not present
    for col in ['land', 'wrong_fragment', 'urgent']:
        if col not in df.columns:
            df[col] = 0  # Default value if missing
    
    return df

def drop_columns(input_file, output_file, allowed_cols):
    """Retains only allowed columns from the dataset and drops rows with missing values."""
    df = pd.read_csv(input_file)
    
    # Generate missing columns
    df = generate_missing_columns(df)
    
    # Keep only allowed columns that exist in the dataset
    df = df[[col for col in allowed_cols if col in df.columns]]
    
    # If 'label' is missing, we add it as a default column
    if 'label' not in df.columns:
        df['label'] = 'unknown'  # Or '0' for a default value
    
    # Drop rows with any missing values
    df.dropna(inplace=True)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Data cleaned and saved to {output_file}")

if __name__ == "__main__":
    input_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/network_data.csv')
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/normalized_data.csv')
    
    drop_columns(input_file, output_file, wireshark_features)

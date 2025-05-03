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
    'Source',  # Ensure Source is retained
    'label' 
]

# Required columns that must be present for the preprocessor
required_columns = ['duration', 'protocol_type', 'service', 'flag']

def generate_missing_columns(df):
    """Generate missing columns based on available information."""
    print("Columns before generation:", df.columns.tolist())  # Debug: Print initial columns
    
    # Preserve or rename Source column with multiple possible names
    source_col = None
    source_variants = ['Source', 'source', 'Source IP', 'src_ip', 'Src']
    for variant in source_variants:
        if variant in df.columns:
            source_col = df[variant].copy()
            df.rename(columns={variant: 'Source'}, inplace=True)
            break
    if source_col is None:
        print("Warning: No Source column variant found, adding placeholder.")
        df['Source'] = 'Unknown'  # Placeholder if no Source variant is found
    
    # Generate 'duration' if 'Time' column exists
    if 'Time' in df.columns:
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')  # Convert Time to datetime
        df['duration'] = df['Time'].diff().fillna(pd.Timedelta(seconds=0))  # Calculate duration
        df['duration'] = df['duration'].dt.total_seconds()  # Convert to seconds
    if 'duration' not in df.columns:
        df['duration'] = 0  # Default value

    # Generate 'src_bytes' and 'dst_bytes' from 'Length' if available
    if 'Length' in df.columns:
        df['src_bytes'] = df['Length']
        df['dst_bytes'] = df['Length']  # Placeholder assumption
    else:
        if 'src_bytes' not in df.columns:
            df['src_bytes'] = 0
        if 'dst_bytes' not in df.columns:
            df['dst_bytes'] = 0

    # Generate 'protocol_type' based on 'Protocol'
    if 'Protocol' in df.columns:
        df['protocol_type'] = df['Protocol'].str.lower()
    if 'protocol_type' not in df.columns:
        df['protocol_type'] = 'tcp'

    # Generate 'service' based on 'Destination Port' or 'Info'
    if 'service' not in df.columns:
        if 'Destination Port' in df.columns:
            df['service'] = df['Destination Port'].map({
                80: 'http', 443: 'https', 21: 'ftp', 22: 'ssh', 23: 'telnet'
            }).fillna('unknown')
        else:
            df['service'] = 'unknown'

    # Generate 'flag' based on 'Info'
    if 'flag' not in df.columns:
        if 'Info' in df.columns:
            df['flag'] = df['Info'].str.lower().apply(lambda x: 'S' if 'syn' in x else ('A' if 'ack' in x else 'O'))
        else:
            df['flag'] = 'O'

    # Add missing columns with default values
    for col in ['land', 'wrong_fragment', 'urgent']:
        if col not in df.columns:
            df[col] = 0

    # Restore or ensure Source column
    if 'Source' not in df.columns and source_col is not None:
        df['Source'] = source_col
    elif 'Source' not in df.columns:
        df['Source'] = 'Unknown'
    
    print("Columns after generation:", df.columns.tolist())  # Debug: Print columns after generation
    return df

def drop_columns(input_file, output_file, allowed_cols):
    """Retains only allowed columns from the dataset and validates required columns."""
    # Try reading with different delimiters and encodings to handle potential issues
    try:
        df = pd.read_csv(input_file, delimiter=',', encoding='utf-8')
    except Exception as e:
        print(f"Error reading CSV with default settings: {e}")
        try:
            df = pd.read_csv(input_file, delimiter=',', encoding='latin1')
            print("Successfully read with latin1 encoding.")
        except Exception as e2:
            raise ValueError(f"Unable to read CSV file: {e2}")

    print("Columns after reading:", df.columns.tolist())  # Debug: Print columns after reading
    
    # Generate missing columns
    df = generate_missing_columns(df)
    
    # Keep only allowed columns that exist in the dataset
    df = df[[col for col in allowed_cols if col in df.columns]]
    
    # If 'label' is missing, add it as a default column
    if 'label' not in df.columns:
        df['label'] = 'unknown'
    
    # Validate required columns
    missing_required = [col for col in required_columns if col not in df.columns]
    if missing_required:
        raise ValueError(f"Required columns missing even after generation: {missing_required}. This does not appear to be a valid Wireshark-exported CSV.")

    # Drop rows with any missing values in required columns
    df.dropna(subset=required_columns, inplace=True)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Data cleaned and saved to {output_file}")
    print("Final columns in output:", df.columns.tolist())  # Debug: Print final columns

if __name__ == "__main__":
    input_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/network_data.csv')
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/normalized_data.csv')
    
    drop_columns(input_file, output_file, wireshark_features)
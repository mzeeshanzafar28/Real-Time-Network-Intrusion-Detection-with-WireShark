import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler

def drop_columns(input_file, output_file, drop_cols):
    """Drops unnecessary columns from the dataset."""
    df = pd.read_csv(input_file)

    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

    original_columns = df.columns.tolist()
    df = df[original_columns]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    df.to_csv(output_file, index=False)
    print(f"Unnecessary columns dropped, new file: {output_file}")

def clean_and_preprocess(output_file, numeric_cols):
    """Cleans, encodes categorical variables, normalizes numerical features, drops rows with empty values, and structures data for ML."""
    df = pd.read_csv(output_file)

    # Drop rows containing any empty (NaN) values
    df.dropna(inplace=True)

    # Encoding categorical variables
    if 'Protocol' in df.columns:
        encoder = LabelEncoder()
        df['Protocol'] = encoder.fit_transform(df['Protocol'])

    # Normalize numerical features
    scaler = StandardScaler()
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = scaler.fit_transform(df[[col]])

    # Assign the new label (0 = Normal, 1 = Malicious, 0 by Default)
    df['Malicious'] = df.apply(lambda row: 1 if 'malicious' in str(row).lower() else 0, axis=1)

    df.to_csv(output_file, index=False)
    print(f"Structured and preprocessed data saved to {output_file}")


if __name__ == "__main__":
    input_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/network_data.csv')
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/normalized_data.csv')

    drop_cols = ['Info']
    numeric_cols = ['Length', 'Time']

    # Step 1: Drop unnecessary columns (output_file is used for next step)
    drop_columns(input_file, output_file, drop_cols)

    # Step 2: Clean, preprocess, encode, normalize, and structure data
    clean_and_preprocess(output_file, numeric_cols)

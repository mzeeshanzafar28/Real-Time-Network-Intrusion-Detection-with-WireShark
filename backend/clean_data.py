import pandas as pd
import os

class DataCleaner:
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
        'Source',
        'label'
    ]

    required_columns = ['duration', 'protocol_type', 'service', 'flag']

    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.df = None

    def generate_missing_columns(self):
        print("Columns before generation:", self.df.columns.tolist())
        
        source_col = None
        source_variants = ['Source', 'source', 'Source IP', 'src_ip', 'Src']
        for variant in source_variants:
            if variant in self.df.columns:
                source_col = self.df[variant].copy()
                self.df.rename(columns={variant: 'Source'}, inplace=True)
                break
        if source_col is None:
            print("Warning: No Source column variant found, adding placeholder.")
            self.df['Source'] = 'Unknown'
        
        if 'Time' in self.df.columns:
            self.df['Time'] = pd.to_datetime(self.df['Time'], errors='coerce')
            self.df['duration'] = self.df['Time'].diff().fillna(pd.Timedelta(seconds=0))
            self.df['duration'] = self.df['duration'].dt.total_seconds()
        if 'duration' not in self.df.columns:
            self.df['duration'] = 0

        if 'Length' in self.df.columns:
            self.df['src_bytes'] = self.df['Length']
            self.df['dst_bytes'] = self.df['Length']
        else:
            if 'src_bytes' not in self.df.columns:
                self.df['src_bytes'] = 0
            if 'dst_bytes' not in self.df.columns:
                self.df['dst_bytes'] = 0

        if 'Protocol' in self.df.columns:
            self.df['protocol_type'] = self.df['Protocol'].str.lower()
        if 'protocol_type' not in self.df.columns:
            self.df['protocol_type'] = 'tcp'

        if 'service' not in self.df.columns:
            if 'Destination Port' in self.df.columns:
                self.df['service'] = self.df['Destination Port'].map({
                    80: 'http', 443: 'https', 21: 'ftp', 22: 'ssh', 23: 'telnet'
                }).fillna('unknown')
            else:
                self.df['service'] = 'unknown'

        if 'flag' not in self.df.columns:
            if 'Info' in self.df.columns:
                self.df['flag'] = self.df['Info'].str.lower().apply(lambda x: 'S' if 'syn' in x else ('A' if 'ack' in x else 'O'))
            else:
                self.df['flag'] = 'O'

        for col in ['land', 'wrong_fragment', 'urgent']:
            if col not in self.df.columns:
                self.df[col] = 0

        if 'Source' not in self.df.columns and source_col is not None:
            self.df['Source'] = source_col
        elif 'Source' not in self.df.columns:
            self.df['Source'] = 'Unknown'
        
        print("Columns after generation:", self.df.columns.tolist())
        return self.df

    def drop_columns(self):
        try:
            self.df = pd.read_csv(self.input_file, delimiter=',', encoding='utf-8')
        except Exception as e:
            print(f"Error reading CSV with default settings: {e}")
            try:
                self.df = pd.read_csv(self.input_file, delimiter=',', encoding='latin1')
                print("Successfully read with latin1 encoding.")
            except Exception as e2:
                raise ValueError(f"Unable to read CSV file: {e2}")

        print("Columns after reading:", self.df.columns.tolist())
        
        self.df = self.generate_missing_columns()
        
        self.df = self.df[[col for col in self.wireshark_features if col in self.df.columns]]
        
        if 'label' not in self.df.columns:
            self.df['label'] = 'unknown'
        
        missing_required = [col for col in self.required_columns if col not in self.df.columns]
        if missing_required:
            raise ValueError(f"Required columns missing even after generation: {missing_required}. This does not appear to be a valid Wireshark-exported CSV.")

        self.df.dropna(subset=self.required_columns, inplace=True)
        
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        self.df.to_csv(self.output_file, index=False)
        print(f"Data cleaned and saved to {self.output_file}")
        print("Final columns in output:", self.df.columns.tolist())

if __name__ == "__main__":
    input_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/network_data.csv')
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../files/normalized_data.csv')
    
    cleaner = DataCleaner(input_file, output_file)
    cleaner.drop_columns()
import pandas as pd
import random
import os

# Define possible values for each column based on the dataset
protocol_types = ['tcp', 'udp', 'icmp']
services = ['http', 'ftp', 'smtp', 'dns', 'ssh']
flags = ['SF', 'S0', 'S1', 'REJ', 'RSTO']
labels = ['normal', 'malicious']

# Function to generate a dummy IPv4 address
def generate_dummy_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

# Function to generate random rows
def generate_random_row(label):
    return {
        'duration': random.randint(1, 100),  # Random duration in seconds
        'protocol_type': random.choice(protocol_types),
        'service': random.choice(services),
        'flag': random.choice(flags),
        'src_bytes': random.randint(100, 5000),  # Random source bytes
        'dst_bytes': random.randint(100, 5000),  # Random destination bytes
        'land': random.choice([0, 1]),  # Random 'land' (0 or 1)
        'wrong_fragment': random.choice([0, 1]),  # Random 'wrong_fragment'
        'urgent': random.choice([0, 1]),  # Random 'urgent'
        'Source': generate_dummy_ip(),  # Add dummy source IP
        'label': label  # 'normal' or 'malicious'
    }

# Generate dummy data with a mix of normal and malicious traffic
dummy_data = []

# Set the number of rows
total_rows = 100
normal_rows = int(total_rows * 0.60)  # 60% normal traffic
malicious_rows = total_rows - normal_rows  # 40% malicious traffic

# Generate normal traffic rows
for _ in range(normal_rows):
    dummy_data.append(generate_random_row('normal'))

# Generate malicious traffic rows
for _ in range(malicious_rows):
    dummy_data.append(generate_random_row('malicious'))

# Shuffle the rows to mix normal and malicious data
random.shuffle(dummy_data)

# Check the first few rows to debug the issue
for i in range(10):  # Print the first 10 rows to verify label distribution
    print(dummy_data[i])

# Convert the list of dictionaries into a DataFrame
df = pd.DataFrame(dummy_data)

# Set the path to save the file (going one dir back, then into 'files' dir)
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_csvs')
os.makedirs(output_dir, exist_ok=True)

# Define the output file path
output_file = os.path.join(output_dir, 'dummy_network_data.csv')

# Save the DataFrame to the CSV file
df.to_csv(output_file, index=False)

print(f"Dummy dataset saved to {output_file}")
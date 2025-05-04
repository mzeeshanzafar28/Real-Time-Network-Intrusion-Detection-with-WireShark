import pandas as pd
import random
import os

class DummyDataGenerator:
    protocol_types = ['tcp', 'udp', 'icmp']
    services = ['http', 'ftp', 'smtp', 'dns', 'ssh']
    flags = ['SF', 'S0', 'S1', 'REJ', 'RSTO']
    labels = ['normal', 'malicious']

    def __init__(self, output_dir, output_filename, total_rows=100):
        self.output_dir = output_dir
        self.output_file = os.path.join(output_dir, output_filename)
        self.total_rows = total_rows
        self.dummy_data = []

    def generate_dummy_ip(self):
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

    def generate_random_row(self, label):
        return {
            'duration': random.randint(1, 100),
            'protocol_type': random.choice(self.protocol_types),
            'service': random.choice(self.services),
            'flag': random.choice(self.flags),
            'src_bytes': random.randint(100, 5000),
            'dst_bytes': random.randint(100, 5000),
            'land': random.choice([0, 1]),
            'wrong_fragment': random.choice([0, 1]),
            'urgent': random.choice([0, 1]),
            'Source': self.generate_dummy_ip(),
            'label': label
        }

    def generate_data(self):
        normal_rows = int(self.total_rows * 0.60)
        malicious_rows = self.total_rows - normal_rows

        for _ in range(normal_rows):
            self.dummy_data.append(self.generate_random_row('normal'))

        for _ in range(malicious_rows):
            self.dummy_data.append(self.generate_random_row('malicious'))

        random.shuffle(self.dummy_data)

        for i in range(10):
            print(self.dummy_data[i])

        df = pd.DataFrame(self.dummy_data)

        os.makedirs(self.output_dir, exist_ok=True)
        df.to_csv(self.output_file, index=False)
        print(f"Dummy dataset saved to {self.output_file}")

if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_csvs')
    generator = DummyDataGenerator(output_dir, 'dummy_network_data.csv')
    generator.generate_data()
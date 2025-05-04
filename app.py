import os
import time
import random
import subprocess
import json
from flask import Flask, render_template, request, redirect, url_for, flash

class NetworkApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'your_secret_key'
        self.UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        self.app.config['UPLOAD_FOLDER'] = self.UPLOAD_FOLDER
        self.ALLOWED_EXTENSIONS = {'csv'}
        self.setup_routes()

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def analyze_file(self, file_path):
        time.sleep(3)

        try:
            backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
            subprocess.run(['python', 'clean_data.py'], cwd=backend_dir, check=True)
            subprocess.run(['python', 'determine.py'], cwd=backend_dir, check=True)
            
            results_file = os.path.join(self.app.config['UPLOAD_FOLDER'], 'analysis_results.json')
            with open(results_file, 'r') as f:
                results = json.load(f)
            print("Results from determine.py:", results)
            return results
        except subprocess.CalledProcessError as e:
            if "Required columns missing" in str(e.output):
                flash("Error: This does not appear to be a valid Wireshark-exported CSV. Missing required columns.")
            else:
                flash(f"Error during analysis: {e}")
            return None
        except Exception as e:
            flash(f"Error during analysis: {e}")
            return None

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/upload', methods=['GET', 'POST'])
        def upload():
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash('No file part in the request.')
                    return redirect(request.url)
                file = request.files['file']
                if file.filename == '':
                    flash('No file selected for uploading.')
                    return redirect(request.url)
                if file and self.allowed_file(file.filename):
                    file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], 'network_data.csv')
                    file.save(file_path)
                    return redirect(url_for('analyze'))
            return render_template('upload.html')

        @self.app.route('/analyze')
        def analyze():
            file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], 'network_data.csv')
            if not os.path.exists(file_path):
                flash('No uploaded file found for analysis.')
                return redirect(url_for('upload'))
            
            results = self.analyze_file(file_path)
            if results is None:
                return redirect(url_for('upload'))
            
            return render_template('results.html', results=results, filename="network_data.csv")

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    network_app = NetworkApp()
    network_app.run()
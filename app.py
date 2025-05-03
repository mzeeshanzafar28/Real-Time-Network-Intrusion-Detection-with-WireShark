import os
import time
import random
import subprocess
import json
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

# Define new upload path
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the directory exists
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_file(file_path):
    time.sleep(3)  # Simulate processing delay

    try:
        backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
        subprocess.run(['python', 'clean_data.py'], cwd=backend_dir, check=True)
        subprocess.run(['python', 'determine.py'], cwd=backend_dir, check=True)
        
        results_file = os.path.join(app.config['UPLOAD_FOLDER'], 'analysis_results.json')
        with open(results_file, 'r') as f:
            results = json.load(f)
        print("Results from determine.py:", results)  # Debugging output
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request.')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'network_data.csv')
            file.save(file_path)
            return redirect(url_for('analyze'))
    return render_template('upload.html')

@app.route('/analyze')
def analyze():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'network_data.csv')
    if not os.path.exists(file_path):
        flash('No uploaded file found for analysis.')
        return redirect(url_for('upload'))
    
    results = analyze_file(file_path)
    if results is None:
        return redirect(url_for('upload'))
    
    return render_template('results.html', results=results, filename="network_data.csv")

if __name__ == '__main__':
    app.run(debug=True)
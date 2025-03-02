import os
import time
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random key
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Dummy analysis function simulating model processing
def analyze_file(file_path):
    time.sleep(3)  # simulate processing delay
    result = {
        "total_packets": random.randint(100, 1000),
        "malicious": random.randint(0, 100),
        "normal": random.randint(50, 900),
        "accuracy": round(random.uniform(0.7, 0.99), 2)
    }
    return result

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
            filename = file.filename  # For production, use secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            flash('File uploaded successfully!')
            return redirect(url_for('analyze', filename=filename))
    return render_template('upload.html')

@app.route('/analyze/<filename>')
def analyze(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    results = analyze_file(file_path)
    return render_template('results.html', results=results, filename=filename)

if __name__ == '__main__':
    app.run(debug=True)

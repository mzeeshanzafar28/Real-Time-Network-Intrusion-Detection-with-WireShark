import os
import time
import random
import subprocess
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

    # Running clean_data.py and determine.py and capturing their output
    try:
        # Change directory to backend before running scripts
        backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
      
        # Run clean_data.py first (you may need to implement the actual logic there)
        subprocess.run(['python', 'clean_data.py'], cwd=backend_dir, check=True)
        
        # Run determine.py to get results
        result = subprocess.check_output(['python', 'determine.py'], cwd=backend_dir).decode('utf-8')
        
        # Process the output (assuming determine.py prints something useful like prediction)
        results = process_determine_output(result)
        print("Results from determine.py:", results)  # Debugging output

    except Exception as e:
        flash(f"Error during analysis: {e}")
        return None  # Return None to avoid breaking the application
    
    return results


def process_determine_output(output):
    # Here, you can parse the output from determine.py and extract the necessary data.
    # Assuming determine.py outputs predictions in a known format, like:
    # Row 1: Predicted label: Malicious, Probability: 0.87
    # Extracting mock data for simplicity:
    results = {
        "total_packets": 100,  # Replace with the actual number of packets from your output
        "malicious": 40,  # Replace with the actual malicious count
        "normal": 60,  # Replace with the actual normal count
        "accuracy": 0.85  # Replace with the actual accuracy
    }
    return results


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
            # Save as 'network_data.csv' in /files directory
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'network_data.csv')
            file.save(file_path)
            # flash('File uploaded successfully as network_data.csv!')
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
        flash("Error during analysis. Please try again.")
        return redirect(url_for('upload'))
    
    return render_template('results.html', results=results, filename="network_data.csv")


if __name__ == '__main__':
    app.run(debug=True)

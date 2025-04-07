# Real-Time-Network-Intrusion-Detection-with-WireShark

1. Create virtual environment:
    `python -m venv venv`
2. Activate the environment:
    On Windows: `venv\Scripts\activate`
    On Linux/Mac: `source venv/bin/activate`
3. Install required packages:
    `pip install -r requirements.txt`
4. Run the flask app:
    `python app.py`
5. Temporary Step (Will address later)|  open another terminal and run after uploading the csv from the web app:
    `python backend/clean_data.py`
6. A new file will be created in the backend folder named `normalized_data.csv`, now run: 
    `python backend/determine.py`
7. Results are on console for now.
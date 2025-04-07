@echo off

REM Check if the venv directory exists
IF EXIST venv\Scripts\activate.bat (

    REM Activate the virtual environment
    call venv\Scripts\activate

    REM Install requirements.txt
    echo Notice: Checking and Installing Requirements.
    pip install -q -r requirements.txt

) ELSE (
    echo Warning: Virtual environment not found. Continuing without activation.
)

REM Run the Python script
python app.py

REM Pause to keep the window open
pause

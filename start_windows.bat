@echo off

REM Check if Python 3.12 is installed
python --version | find "3.12" >nul
if errorlevel 1 (
    echo Python 3.12 is not installed or not in PATH.
    echo Please install Python 3.12 and try again.
    pause
    exit /b
)

REM Check if the virtual environment already exists
if not exist "venv\Scripts\activate.bat" (
    REM Create the virtual environment
    echo Creating Python 3.12 virtual environment...
    python -m venv venv

    REM Activate the virtual environment
    call venv\Scripts\activate

    REM Upgrade pip to the latest version
    echo Upgrading pip...
    python -m pip install --upgrade pip

    REM Install required packages
    echo Installing required packages...
    pip install customtkinter keyring pillow requests

    REM Deactivate the virtual environment
    echo Deactivating the virtual environment after setup...
    python gimmich.py
    deactivate
) else (
    echo Virtual environment already exists. Skipping setup...
)

REM Activate the virtual environment
echo Activating the virtual environment...
call venv\Scripts\activate

REM Run the Python program
echo Running gimmich.py...
python gimmich.py

REM Deactivate the virtual environment after running the program
echo Deactivating the virtual environment...
deactivate

echo Setup and execution complete!
pause

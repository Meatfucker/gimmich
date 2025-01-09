#!/bin/bash

# Check if Python 3.12 is installed
if ! python3.12 --version &> /dev/null; then
  echo "Python 3.12 is not installed or not in PATH."
  echo "Please install Python 3.12 and try again."
  exit 1
fi

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
  # Create the virtual environment
  echo "Creating Python 3.12 virtual environment..."
  python3.12 -m venv venv

  # Activate the virtual environment
  echo "Activating the virtual environment..."
  source venv/bin/activate

  # Upgrade pip to the latest version
  echo "Upgrading pip..."
  pip install --upgrade pip

  # Install required packages
  echo "Installing required packages..."
  pip install customtkinter keyring pillow requests

  # Deactivate the virtual environment after setup
  echo "Deactivating the virtual environment after setup..."
  python gimmich.py
  deactivate
else
  echo "Virtual environment already exists. Skipping setup..."
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Run the Python program
echo "Running gimmich.py..."
python gimmich.py

# Deactivate the virtual environment after running the program
echo "Deactivating the virtual environment..."
deactivate

echo "Setup and execution complete!"

#!/usr/bin/env python3
"""
Setup script for Flask Authentication Example
This script helps resolve compatibility issues with older Python versions.
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 6):
        print("Warning: Python 3.6+ is recommended for best compatibility.")
        print("Using alternative hashing method for older Python versions.")
        return False
    return True

def install_requirements():
    """Install requirements with compatible versions."""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def main():
    print("Flask Authentication Setup")
    print("=" * 30)
    
    # Check Python version
    is_compatible = check_python_version()
    
    # Install requirements
    if install_requirements():
        print("\nSetup completed successfully!")
        print("\nTo run the application:")
        print("python app.py")
        print("\nThen visit: http://localhost:5000")
    else:
        print("\nSetup failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 
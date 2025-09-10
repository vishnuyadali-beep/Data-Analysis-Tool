#!/usr/bin/env python3
"""
One-click Python environment setup for data analysis tools
Run this script on any new device to automatically set up everything needed
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    print("🚀 Setting up Python Data Analysis Environment...")
    print("=" * 50)
    
    # Required packages for your data analysis tool
    packages = [
        "pandas",
        "numpy", 
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "openpyxl",
        "xlrd",
        "xlsxwriter",
        "customtkinter"
    ]
    
    print(f"📦 Installing {len(packages)} packages...")
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Setup complete! {success_count}/{len(packages)} packages installed successfully")
    
    if success_count == len(packages):
        print("🎉 Your data analysis environment is ready!")
        print("\nYou can now run:")
        print("python simple_gui_analyzer.py")
    else:
        print("⚠️  Some packages failed to install. Please check the errors above.")

if __name__ == "__main__":
    main()
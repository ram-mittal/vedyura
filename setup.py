#!/usr/bin/env python3
"""
Vedyura Setup Script
This script helps set up the Vedyura application with initial data and configuration.
"""

import os
import json
import sys

def create_data_directory():
    """Create data directory if it doesn't exist"""
    if not os.path.exists('data'):
        os.makedirs('data')
        print("✅ Created data directory")
    else:
        print("✅ Data directory already exists")

def check_required_files():
    """Check if all required data files exist"""
    required_files = [
        'data/users.json',
        'data/requests.json',
        'data/food_database.json',
        'data/recipes.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All required data files are present")
        return True

def display_credentials():
    """Display login credentials for demo users"""
    print("\n" + "="*50)
    print("🔐 DEMO LOGIN CREDENTIALS")
    print("="*50)
    
    print("\n👤 PATIENT ACCOUNTS:")
    print("   Username: patient1  | Password: password123")
    print("   Username: patient2  | Password: patient456")
    print("   Username: patient3  | Password: demo123")
    
    print("\n👨‍⚕️ DOCTOR ACCOUNTS:")
    print("   Username: doctor1   | Password: doctor123")
    print("   Username: doctor2   | Password: ayurveda456")
    print("   Username: doctor3   | Password: wellness789")
    
    print("\n" + "="*50)

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'flask',
        'opencv-python',
        'numpy',
        'scipy',
        'fpdf2',
        'pandas'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def main():
    """Main setup function"""
    print("🌿 Vedyura Setup Script")
    print("=" * 30)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create data directory
    create_data_directory()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check required files
    files_ok = check_required_files()
    
    # Display credentials
    display_credentials()
    
    # Final status
    print("\n" + "="*50)
    if deps_ok and files_ok:
        print("🎉 SETUP COMPLETE!")
        print("✅ Ready to run: python app.py")
        print("🌐 Then visit: http://localhost:5000")
    else:
        print("⚠️  SETUP INCOMPLETE")
        print("Please resolve the issues above before running the application.")
    print("="*50)

if __name__ == "__main__":
    main()
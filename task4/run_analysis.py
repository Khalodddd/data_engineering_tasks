#!/usr/bin/env python3
"""
Run this script to process all datasets and start the dashboard
"""

import subprocess
import sys
import os

def check_data_folders():
    """Check if data folders exist"""
    datasets = ['DATA1', 'DATA2', 'DATA3']
    print("🔍 Checking for data folders...")
    
    for dataset in datasets:
        data_path = os.path.join("data", dataset)
        if os.path.exists(data_path):
            print(f"   ✅ Found: {data_path}")
            # Check for required files
            required_files = ['orders.csv', 'books.csv', 'users.csv']
            for file in required_files:
                file_path = os.path.join(data_path, file)
                if os.path.exists(file_path):
                    print(f"      ✅ {file}")
                else:
                    print(f"      ❌ Missing: {file}")
        else:
            print(f"   ❌ Missing: {data_path}")
    
    print("")

def main():
    print("🚀 Starting Bookstore Sales Analysis")
    print("=" * 50)
    
    # Check if data folders exist
    check_data_folders()
    
    # Run analysis
    print("📊 Processing datasets...")
    try:
        import analysis
        analysis.main()
        print("✅ Analysis completed successfully!")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return
    
    # Start dashboard
    print("🌐 Starting dashboard...")
    print("📋 Open your browser and go to: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")

if __name__ == "__main__":
    main()
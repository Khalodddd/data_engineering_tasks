import os
import subprocess
import sys

def check_and_install_dependencies():
    """Check if all required packages are installed"""
    required_packages = ['pandas', 'plotly', 'pyyaml', 'pyarrow']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 Installing missing packages: {missing_packages}")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install"
        ] + missing_packages)
        return result.returncode == 0
    return True

def process_data():
    """Run the data processing script"""
    print("🔄 Processing data...")
    
    # Try different possible paths for process_data.py
    possible_paths = [
        "process_data.py",
        "./process_data.py",
        "/mount/src/data_engineering_tasks/task4/process_data.py"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found process_data.py at: {path}")
            result = subprocess.run([sys.executable, path], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Data processed successfully!")
                return True
            else:
                print(f"❌ Data processing failed: {result.stderr}")
                return False
    
    print("❌ Could not find process_data.py")
    return False

def main():
    print("=" * 50)
    print("🚀 Bookstore Analytics - Setup & Launch")
    print("=" * 50)
    
    # Step 1: Check dependencies
    if not check_and_install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # Step 2: Process data if output doesn't exist
    if not os.path.exists("./output"):
        if not process_data():
            print("❌ Data processing failed, cannot continue")
            return
    else:
        print("✅ Output data already exists")
    
    # Step 3: Launch the dashboard
    print("🎯 Launching dashboard...")
    
    # Try different possible paths for app_streamlit.py
    possible_app_paths = [
        "app_streamlit.py",
        "./app_streamlit.py", 
        "/mount/src/data_engineering_tasks/task4/app_streamlit.py"
    ]
    
    for path in possible_app_paths:
        if os.path.exists(path):
            print(f"✅ Found app_streamlit.py at: {path}")
            print("🌐 Starting Streamlit server...")
            subprocess.run(["streamlit", "run", path, "--server.port=8501", "--server.address=0.0.0.0"])
            return
    
    print("❌ Could not find app_streamlit.py")

if __name__ == "__main__":
    main()
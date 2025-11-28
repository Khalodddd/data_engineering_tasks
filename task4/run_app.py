import os
import subprocess
import streamlit as st
import sys

def install_requirements():
    """Install requirements if needed"""
    try:
        import pandas
        return True
    except ImportError:
        st.info("📦 Installing required packages...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            st.success("✅ Packages installed successfully!")
            return True
        else:
            st.error(f"❌ Package installation failed: {result.stderr}")
            return False

def main():
    st.set_page_config(page_title="Bookstore Analytics", layout="wide")
    
    # First, install requirements
    if not install_requirements():
        return
    
    # Then process data if needed
    if not os.path.exists("./output"):
        st.info("🔄 Processing data for the first time...")
        
        process_file = "/mount/src/data_engineering_tasks/task4/process_data.py"
        
        if os.path.exists(process_file):
            result = subprocess.run(["python", process_file], capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ Data processed successfully! Starting dashboard...")
                st.rerun()
            else:
                st.error(f"❌ Data processing failed: {result.stderr}")
                # Show what packages are available
                st.write("Checking available packages...")
                subprocess.run(["pip", "list"])
        else:
            st.error("❌ Could not find process_data.py file!")
            return
    
    # Now run the Streamlit app
    st.info("🚀 Starting dashboard...")
    
    app_file = "/mount/src/data_engineering_tasks/task4/app_streamlit.py"
    
    if os.path.exists(app_file):
        subprocess.run(["streamlit", "run", app_file])
    else:
        st.error("❌ Could not find app_streamlit.py file!")

if __name__ == "__main__":
    main()
import os
import subprocess
import streamlit as st

def main():
    st.set_page_config(page_title="Bookstore Analytics", layout="wide")
    
    # First, process the data if needed
    if not os.path.exists("./output"):
        st.info("🔄 Processing data for the first time...")
        
        # Try multiple possible paths for process_data.py
        possible_paths = [
            "./process_data.py",
            "process_data.py", 
            "/mount/src/data_engineering_tasks/process_data.py",
            "/mount/src/data_engineering_tasks/task4/process_data.py"
        ]
        
        process_file = None
        for path in possible_paths:
            if os.path.exists(path):
                process_file = path
                st.success(f"✅ Found process_data.py at: {path}")
                break
        
        if process_file:
            result = subprocess.run(["python", process_file], capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ Data processed successfully! Starting dashboard...")
                st.rerun()
            else:
                st.error(f"❌ Data processing failed: {result.stderr}")
        else:
            st.error("❌ Could not find process_data.py file!")
            st.write("Available files:", os.listdir('.'))
            return
    
    # Now run the Streamlit app
    st.info("🚀 Starting dashboard...")
    
    # Try multiple possible paths for app_streamlit.py
    app_paths = [
        "./app_streamlit.py",
        "app_streamlit.py",
        "/mount/src/data_engineering_tasks/app_streamlit.py", 
        "/mount/src/data_engineering_tasks/task4/app_streamlit.py"
    ]
    
    app_file = None
    for path in app_paths:
        if os.path.exists(path):
            app_file = path
            st.success(f"✅ Found app_streamlit.py at: {path}")
            break
    
    if app_file:
        subprocess.run(["streamlit", "run", app_file])
    else:
        st.error("❌ Could not find app_streamlit.py file!")

if __name__ == "__main__":
    main()
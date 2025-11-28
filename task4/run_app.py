import os
import subprocess
import streamlit as st

def main():
    # First, process the data if needed
    if not os.path.exists("./output"):
        st.info("🔄 Processing data for the first time...")
        result = subprocess.run(["python", "process_data.py"], capture_output=True, text=True)
        if result.returncode == 0:
            st.success("✅ Data processed successfully! Starting dashboard...")
        else:
            st.error(f"❌ Data processing failed: {result.stderr}")
            return
    
    # Now run the Streamlit app
    st.info("🚀 Starting dashboard...")
    subprocess.run(["streamlit", "run", "app_streamlit.py"])

if __name__ == "__main__":
    main()
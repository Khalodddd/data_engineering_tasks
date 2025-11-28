import os
import json
import pandas as pd

def check_structure():
    print("🔍 CHECKING FOLDER STRUCTURE AND FILES")
    print("=" * 50)
    
    # Get current working directory
    current_dir = os.getcwd()
    print(f"📁 Current Directory: {current_dir}")
    print()
    
    # List all files and folders in current directory
    print("📂 Contents of current directory:")
    print("-" * 30)
    try:
        items = os.listdir('.')
        for item in sorted(items):
            item_path = os.path.join('.', item)
            if os.path.isdir(item_path):
                print(f"📁 {item}/")
            else:
                print(f"📄 {item}")
    except Exception as e:
        print(f"❌ Error listing directory: {e}")
    print()
    
    # Check for output directory
    output_dirs_to_check = ['./output', 'output', '../output', './task4/output']
    
    for output_dir in output_dirs_to_check:
        print(f"🔎 Checking: {output_dir}")
        if os.path.exists(output_dir):
            print(f"✅ EXISTS: {output_dir}")
            
            # List contents of output directory
            try:
                output_items = os.listdir(output_dir)
                print(f"   Contents of {output_dir}:")
                print("   " + "-" * 25)
                for item in sorted(output_items):
                    item_path = os.path.join(output_dir, item)
                    if os.path.isdir(item_path):
                        print(f"   📁 {item}/")
                    else:
                        size = os.path.getsize(item_path)
                        print(f"   📄 {item} ({size} bytes)")
            except Exception as e:
                print(f"   ❌ Error listing {output_dir}: {e}")
            
            # Check for specific data files
            print()
            print("   🔍 Checking for data files:")
            datasets = ["DATA1", "DATA2", "DATA3"]
            for dataset in datasets:
                summary_file = os.path.join(output_dir, f"{dataset}_summary.json")
                revenue_file = os.path.join(output_dir, f"{dataset}_daily_revenue.csv")
                
                print(f"   {dataset}:")
                print(f"     📊 {summary_file} - EXISTS: {os.path.exists(summary_file)}")
                if os.path.exists(summary_file):
                    try:
                        with open(summary_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        print(f"     ✅ Can read JSON - Keys: {list(data.keys())}")
                    except Exception as e:
                        print(f"     ❌ Error reading JSON: {e}")
                
                print(f"     📈 {revenue_file} - EXISTS: {os.path.exists(revenue_file)}")
                if os.path.exists(revenue_file):
                    try:
                        df = pd.read_csv(revenue_file)
                        print(f"     ✅ Can read CSV - Shape: {df.shape}, Columns: {list(df.columns)}")
                    except Exception as e:
                        print(f"     ❌ Error reading CSV: {e}")
                print()
            
            break  # Stop after finding first valid output directory
        else:
            print(f"❌ NOT FOUND: {output_dir}")
            print()
    
    # Check file permissions
    print("🔐 Checking file permissions:")
    print("-" * 30)
    test_files = [
        './output/DATA1_summary.json',
        'output/DATA1_summary.json', 
        './app_streamlit.py',
        'app_streamlit.py'
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            try:
                with open(test_file, 'r') as f:
                    f.read(100)  # Try to read first 100 bytes
                print(f"✅ READABLE: {test_file}")
            except Exception as e:
                print(f"❌ NOT READABLE: {test_file} - Error: {e}")
        else:
            print(f"📭 NOT FOUND: {test_file}")
    
    print()
    print("=" * 50)
    print("🎯 RECOMMENDATIONS:")
    
    # Generate recommendations based on findings
    if not any(os.path.exists(output_dir) for output_dir in output_dirs_to_check):
        print("❌ No output directory found!")
        print("   → Make sure 'output/' folder is in your repository")
        print("   → Run 'python process_data.py' locally first")
        print("   → Commit and push the output folder to GitHub")
    else:
        print("✅ Output directory found!")
        print("   → Check if all required files exist")
        print("   → Verify file permissions")
        print("   → Check Streamlit Cloud deployment logs")

if __name__ == "__main__":
    check_structure()
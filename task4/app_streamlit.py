import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

OUTPUT_DIR = "./output"

st.set_page_config(page_title="Bookstore Analytics", layout="wide")
st.title("📊 Bookstore Analytics")

# Check if data exists
if not os.path.exists(OUTPUT_DIR):
    st.error("❌ No processed data found. Please run process_data.py first.")
    st.stop()

# Load data with error handling
datasets = {}
for dataset in ["DATA1", "DATA2", "DATA3"]:
    summary_file = os.path.join(OUTPUT_DIR, f"{dataset}_summary.json")
    revenue_file = os.path.join(OUTPUT_DIR, f"{dataset}_daily_revenue.csv")
    
    try:
        if os.path.exists(summary_file):
            with open(summary_file, "r", encoding="utf-8") as f:
                summary_data = json.load(f)
            
            revenue_data = None
            if os.path.exists(revenue_file):
                revenue_data = pd.read_csv(revenue_file)
            
            datasets[dataset] = {
                "summary": summary_data,
                "revenue_data": revenue_data
            }
    except Exception as e:
        st.error(f"Error loading {dataset}: {str(e)}")

if not datasets:
    st.error("❌ No datasets available. Please check data processing.")
    st.stop()

st.success(f"✅ {len(datasets)} dataset(s) loaded successfully!")

# Create tabs
tab_names = ["COMPARISON"] + [f"{dataset}" for dataset in datasets.keys()]
tabs = st.tabs(tab_names)

# Comparison Tab
with tabs[0]:
    st.header("📊 Dataset Comparison")
    
    cols = st.columns(len(datasets))
    for i, (dataset, data) in enumerate(datasets.items()):
        summary = data["summary"]
        with cols[i]:
            st.subheader(dataset)
            st.metric("Total Revenue", f"${summary.get('top_customer_total_spent', 0):,}")
            st.metric("Unique Users", summary.get('unique_real_users', 0))
            st.metric("Author Sets", summary.get('unique_author_sets', 'N/A'))

# Individual Dataset Tabs
for i, (dataset, data) in enumerate(datasets.items(), 1):
    with tabs[i]:
        summary = data["summary"]
        st.header(f"📁 {dataset} Analysis")
        
        # Top 5 Revenue Days - REQUIRED
        st.subheader("🎯 Top 5 Revenue Days (YYYY-MM-dd)")
        top5_days = summary.get("top5_days", [])
        if top5_days:
            for j, day in enumerate(top5_days[:5], 1):
                date = day.get('date', 'Unknown')
                revenue = day.get('paid_price', 0)
                st.write(f"**#{j} {date}**: ${revenue:,.2f}")
        else:
            st.info("No revenue data available")
        
        # Key Metrics - REQUIRED
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            # Unique Users - REQUIRED
            st.metric("👥 Unique Users", summary.get('unique_real_users', 0))
        with col2:
            # Unique Author Sets - REQUIRED  
            st.metric("📚 Author Sets", summary.get('unique_author_sets', 'N/A'))
        with col3:
            # Most Popular Author - REQUIRED
            authors = summary.get("most_popular_authors", [])
            display_author = authors[0] if authors else "No data"
            st.metric("🏆 Popular Author", display_author)
        with col4:
            # Best Buyer Spending - REQUIRED
            st.metric("💰 Top Spender", f"${summary.get('top_customer_total_spent', 0):,}")
        
        # Best Buyer with IDs - REQUIRED
        st.subheader("👑 Best Buyer Details")
        buyer_ids = summary.get("top_customer_user_ids", [])
        if buyer_ids:
            st.write(f"**User IDs**: {buyer_ids}")
            st.write(f"**Total Spent**: ${summary.get('top_customer_total_spent', 0):,}")
        else:
            st.info("No buyer data available")
        
        # Daily Revenue Chart - REQUIRED
        if data["revenue_data"] is not None and not data["revenue_data"].empty:
            st.subheader("📈 Daily Revenue Chart")
            df = data["revenue_data"]
            try:
                fig = px.line(df, x='date', y='paid_price', 
                            title=f"{dataset} - Daily Revenue Trend",
                            labels={'paid_price': 'Revenue ($)', 'date': 'Date'})
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating chart: {str(e)}")
        else:
            st.info("No revenue chart data available")

st.info("All data processed from orders.parquet, books.yaml, and users.csv")
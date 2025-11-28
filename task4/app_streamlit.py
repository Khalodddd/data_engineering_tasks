import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

OUTPUT_DIR = "./output"

# Professional Page Configuration
st.set_page_config(
    page_title="Bookstore Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .dataset-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .top-day-card {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .customer-card {
        background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
        color: #2c3e50;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 Bookstore Analytics Dashboard</h1>', unsafe_allow_html=True)

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
                if 'paid_price' in revenue_data.columns:
                    revenue_data['paid_price'] = pd.to_numeric(revenue_data['paid_price'], errors='coerce')
            
            datasets[dataset] = {
                "summary": summary_data,
                "revenue_data": revenue_data
            }
    except Exception as e:
        st.error(f"Error loading {dataset}: {str(e)}")

if not datasets:
    st.error("❌ No datasets available. Please check data processing.")
    st.stop()

# Success message
st.success(f"✅ {len(datasets)} dataset(s) loaded successfully! Dashboard is ready for analysis.")

# Create professional tabs
tab_names = ["📊 COMPARISON DASHBOARD"] + [f"📁 {dataset}" for dataset in datasets.keys()]
tabs = st.tabs(tab_names)

# Comparison Tab - Professional Layout
with tabs[0]:
    st.markdown("## 📈 Multi-Dataset Performance Overview")
    
    # KPI Cards Row
    st.markdown("### 🎯 Key Performance Indicators")
    cols = st.columns(len(datasets))
    
    for i, (dataset, data) in enumerate(datasets.items()):
        summary = data["summary"]
        with cols[i]:
            total_revenue = data["revenue_data"]['paid_price'].sum() if data["revenue_data"] is not None else 0
            
            st.markdown(f"""
            <div class="metric-card">
                <h3>{dataset}</h3>
                <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;">${total_revenue:,.0f}</p>
                <p>Total Revenue</p>
                <p style="font-size: 1.1rem; margin: 0.2rem 0;">👥 {summary.get('unique_real_users', 0):,} Users</p>
                <p style="font-size: 1.1rem; margin: 0.2rem 0;">📚 {summary.get('unique_author_sets', 0)} Author Sets</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Revenue Comparison Chart
    st.markdown("### 📊 Revenue Trends Comparison")
    fig_comparison = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    for idx, (dataset, data) in enumerate(datasets.items()):
        if data["revenue_data"] is not None and not data["revenue_data"].empty:
            df = data["revenue_data"].copy()
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date', 'paid_price'])
            
            if not df.empty:
                fig_comparison.add_trace(go.Scatter(
                    x=df['date'], 
                    y=df['paid_price'],
                    name=dataset,
                    line=dict(width=3, color=colors[idx]),
                    mode='lines'
                ))
    
    fig_comparison.update_layout(
        title="Daily Revenue Trends Across All Datasets",
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(fig_comparison, use_container_width=True)

# Individual Dataset Tabs - Professional Layout
for i, (dataset, data) in enumerate(datasets.items(), 1):
    with tabs[i]:
        summary = data["summary"]
        
        # Header with dataset info
        st.markdown(f"## 📋 {dataset} - Detailed Analysis")
        
        # Top Row - Key Metrics
        st.markdown("### 🎯 Performance Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            unique_users = summary.get('unique_real_users', 0)
            st.markdown(f"""
            <div class="metric-card">
                <h4>👥 Unique Users</h4>
                <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0;">{unique_users:,}</p>
                <p>After user reconciliation</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            author_sets = summary.get('unique_author_sets', 0)
            st.markdown(f"""
            <div class="metric-card">
                <h4>📚 Author Sets</h4>
                <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0;">{author_sets}</p>
                <p>Unique combinations</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            authors = summary.get("most_popular_authors", [])
            display_author = authors[0] if authors else "No data"
            st.markdown(f"""
            <div class="metric-card">
                <h4>🏆 Popular Author</h4>
                <p style="font-size: 1.3rem; font-weight: bold; margin: 0.5rem 0;">{display_author}</p>
                <p>Most frequent in catalog</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_spent = summary.get('top_customer_total_spent', 0)
            st.markdown(f"""
            <div class="metric-card">
                <h4>💰 Top Spender</h4>
                <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;">${total_spent:,.0f}</p>
                <p>Total customer spending</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Two Column Layout for Details
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Top 5 Revenue Days - Professional Cards
            st.markdown("### 🎯 Top 5 Revenue Days")
            top5_days = summary.get("top5_days", [])
            if top5_days:
                for j, day in enumerate(top5_days[:5], 1):
                    date = day.get('date', 'Unknown')
                    revenue = day.get('paid_price', 0)
                    st.markdown(f"""
                    <div class="top-day-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="font-size: 1.1em;">#{j} {date}</strong>
                            </div>
                            <div style="font-size: 1.2em; font-weight: bold;">
                                ${revenue:,.2f}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📊 No revenue day data available")
        
        with col_right:
            # Best Buyer Information - Professional Card
            st.markdown("### 👑 Best Buyer Details")
            buyer_ids = summary.get("top_customer_user_ids", [])
            total_spent = summary.get('top_customer_total_spent', 0)
            
            if buyer_ids:
                st.markdown(f"""
                <div class="customer-card">
                    <h4 style="margin: 0 0 1rem 0;">🏆 Top Customer</h4>
                    <p style="font-size: 1.1em; margin: 0.5rem 0;"><strong>User IDs:</strong> {', '.join(map(str, buyer_ids))}</p>
                    <p style="font-size: 1.3em; font-weight: bold; margin: 0.5rem 0; color: #27ae60;">
                        Total Spent: ${total_spent:,.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("👤 No buyer data available")
        
        # Revenue Chart - Professional Styling
        if data["revenue_data"] is not None and not data["revenue_data"].empty:
            st.markdown("### 📈 Revenue Analytics")
            
            df = data["revenue_data"].copy()
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date', 'paid_price'])
            
            if not df.empty:
                # Create area chart for better visual appeal
                fig = px.area(df, x='date', y='paid_price', 
                            title=f"{dataset} - Daily Revenue Trend",
                            labels={'paid_price': 'Revenue ($)', 'date': 'Date'})
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#2c3e50"),
                    height=400,
                    hovermode='x unified',
                    xaxis=dict(showgrid=True, gridcolor='lightgray'),
                    yaxis=dict(showgrid=True, gridcolor='lightgray')
                )
                
                fig.update_traces(
                    line=dict(color='#3498db', width=3),
                    fillcolor='rgba(52, 152, 219, 0.3)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Revenue Statistics
                st.markdown("#### 💹 Revenue Statistics")
                stat_cols = st.columns(4)
                
                with stat_cols[0]:
                    total_rev = df['paid_price'].sum()
                    st.metric("Total Revenue", f"${total_rev:,.0f}")
                
                with stat_cols[1]:
                    avg_daily = df['paid_price'].mean()
                    st.metric("Avg Daily", f"${avg_daily:,.0f}")
                
                with stat_cols[2]:
                    highest_day = df['paid_price'].max()
                    st.metric("Peak Day", f"${highest_day:,.0f}")
                
                with stat_cols[3]:
                    days_count = len(df)
                    st.metric("Days Tracked", days_count)
            else:
                st.info("📊 No valid revenue data for visualization")
        else:
            st.info("📊 No revenue chart data available")

# Professional Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 2rem 0;">
    <p><strong>Bookstore Analytics Platform</strong> • Business Intelligence Dashboard</p>
    <p>Data Sources: orders.parquet, books.yaml, users.csv • Processed with Python</p>
</div>
""", unsafe_allow_html=True)
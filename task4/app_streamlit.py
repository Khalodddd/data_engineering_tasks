import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

OUTPUT_DIR = "./output"

# Page configuration
st.set_page_config(
    page_title="Bookstore Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .dataset-header {
        font-size: 2rem;
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #3498db;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .top-day-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .author-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .customer-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 10px 10px 0 0;
        gap: 1rem;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3498db !important;
        color: white !important;
    }
    .comparison-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 Bookstore Analytics Dashboard</h1>', unsafe_allow_html=True)

# Load all datasets for comparison
all_datasets = {}
datasets_available = []

for dataset in ["DATA1", "DATA2", "DATA3"]:
    summary_file = os.path.join(OUTPUT_DIR, f"{dataset}_summary.json")
    revenue_file = os.path.join(OUTPUT_DIR, f"{dataset}_daily_revenue.csv")
    
    if os.path.exists(summary_file):
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                summary_data = json.load(f)
            
            revenue_data = None
            if os.path.exists(revenue_file):
                revenue_data = pd.read_csv(revenue_file)
                # Ensure numeric conversion for revenue data
                if 'paid_price' in revenue_data.columns:
                    revenue_data['paid_price'] = pd.to_numeric(revenue_data['paid_price'], errors='coerce')
            
            all_datasets[dataset] = {
                "summary": summary_data,
                "revenue_data": revenue_data
            }
            datasets_available.append(dataset)
            
        except Exception as e:
            st.error(f"Error loading {dataset}: {str(e)}")
    else:
        st.warning(f"⚠️ No data found for {dataset}")

if datasets_available:
    st.success(f"🎉 {len(datasets_available)} dataset(s) processed successfully! Data is ready for analysis.")
else:
    st.error("❌ No datasets available. Please check if data processing completed successfully.")
    st.stop()

# Create tabs for each dataset with comparison tab
tab_names = ["📊 COMPARISON"] + [f"📚 {dataset}" for dataset in datasets_available]
tabs = st.tabs(tab_names)

# Helper function to safely get numeric values
def safe_get(data, key, default=0):
    value = data.get(key, default)
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default

# Comparison Tab
with tabs[0]:
    st.markdown('<div class="dataset-header">📊 Multi-Dataset Comparison</div>', unsafe_allow_html=True)
    
    # Key comparison metrics
    st.subheader("🔍 Performance Comparison")
    
    # Create comparison metrics
    comparison_data = []
    for dataset_name in datasets_available:
        data = all_datasets[dataset_name]
        summary = data["summary"]
        
        # Calculate total revenue from revenue data if available, otherwise from summary
        if data["revenue_data"] is not None and 'paid_price' in data["revenue_data"].columns:
            total_revenue = data["revenue_data"]['paid_price'].sum()
        else:
            total_revenue = safe_get(summary, 'total_revenue', 0)
        
        # Calculate average daily revenue
        if data["revenue_data"] is not None and 'paid_price' in data["revenue_data"].columns:
            avg_daily_revenue = data["revenue_data"]['paid_price'].mean()
        else:
            avg_daily_revenue = 0
        
        comparison_data.append({
            "Dataset": dataset_name,
            "Total Revenue": total_revenue,
            "Unique Users": safe_get(summary, 'unique_real_users', 0),
            "Unique Author Sets": safe_get(summary, 'unique_author_sets', 0),
            "Top Customer Spend": safe_get(summary, 'top_customer_total_spent', 0),
            "Average Daily Revenue": avg_daily_revenue
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Display metrics in columns
    cols = st.columns(len(comparison_data))
    for idx, (col, row) in enumerate(zip(cols, comparison_data)):
        with col:
            st.markdown(f'''
            <div class="comparison-metric">
                <h3>{row['Dataset']}</h3>
                <p style="font-size: 1.2rem; margin:0.2rem 0;">💰 ${row['Total Revenue']:,.0f}</p>
                <small>Total Revenue</small>
                <p style="font-size: 1.1rem; margin:0.2rem 0;">👥 {row['Unique Users']:,}</p>
                <small>Unique Users</small>
            </div>
            ''', unsafe_allow_html=True)
    
    # Revenue comparison chart
    st.subheader("📈 Revenue Comparison")
    
    # Check if we have revenue data for any dataset
    has_revenue_data = any(data["revenue_data"] is not None for data in all_datasets.values())
    
    if has_revenue_data:
        fig_comparison = go.Figure()
        colors = ['#3498db', '#e74c3c', '#27ae60']
        
        for idx, dataset_name in enumerate(datasets_available):
            data = all_datasets[dataset_name]
            if data["revenue_data"] is not None and 'date' in data["revenue_data"].columns:
                df = data["revenue_data"].copy()
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.dropna(subset=['date', 'paid_price'])
                
                if not df.empty:
                    fig_comparison.add_trace(go.Scatter(
                        x=df['date'], 
                        y=df['paid_price'],
                        name=dataset_name,
                        line=dict(width=3, color=colors[idx % len(colors)]),
                        fill='tozeroy',
                        opacity=0.3
                    ))
        
        if len(fig_comparison.data) > 0:
            fig_comparison.update_layout(
                title="Daily Revenue Trends Across All Datasets",
                xaxis_title="Date",
                yaxis_title="Revenue (USD $)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
        else:
            st.info("📊 No valid revenue data available for trend comparison")
    else:
        st.info("📊 Revenue data not available for trend comparison")
    
    # Performance metrics comparison
    st.subheader("📊 Performance Metrics")
    
    # Create bar charts for key metrics
    if len(datasets_available) > 1:
        metric_cols = st.columns(2)
        
        with metric_cols[0]:
            # Total Revenue comparison
            fig_revenue = px.bar(comparison_df, x='Dataset', y='Total Revenue',
                               title='Total Revenue by Dataset',
                               color='Dataset',
                               color_discrete_sequence=px.colors.qualitative.Bold)
            fig_revenue.update_layout(showlegend=False, height=300)
            fig_revenue.update_traces(hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>')
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        with metric_cols[1]:
            # Unique Users comparison
            fig_users = px.bar(comparison_df, x='Dataset', y='Unique Users',
                             title='Unique Users by Dataset',
                             color='Dataset',
                             color_discrete_sequence=px.colors.qualitative.Set2)
            fig_users.update_layout(showlegend=False, height=300)
            fig_users.update_traces(hovertemplate='<b>%{x}</b><br>Users: %{y:,}<extra></extra>')
            st.plotly_chart(fig_users, use_container_width=True)
    
    # Dataset rankings
    st.subheader("🏆 Dataset Rankings")
    
    # Calculate rankings
    rankings_data = []
    metrics = ['Total Revenue', 'Unique Users', 'Average Daily Revenue', 'Top Customer Spend']
    
    for metric in metrics:
        if metric in comparison_df.columns:
            ranked = comparison_df.nlargest(len(comparison_df), metric)
            for i, (_, row) in enumerate(ranked.iterrows()):
                rankings_data.append({
                    'Metric': metric,
                    'Dataset': row['Dataset'],
                    'Rank': i + 1,
                    'Value': row[metric]
                })
    
    if rankings_data:
        rankings_df = pd.DataFrame(rankings_data)
        
        # Display rankings in a nice format
        rank_cols = st.columns(len(metrics))
        for idx, metric in enumerate(metrics):
            with rank_cols[idx]:
                st.markdown(f"**{metric}**")
                metric_data = rankings_df[rankings_df['Metric'] == metric].sort_values('Rank')
                for _, row in metric_data.iterrows():
                    medal = "🥇" if row['Rank'] == 1 else "🥈" if row['Rank'] == 2 else "🥉" if row['Rank'] == 3 else f"{row['Rank']}."
                    if 'Revenue' in metric or 'Spend' in metric:
                        value = f"${row['Value']:,.0f}" if row['Value'] > 0 else "$0"
                    else:
                        value = f"{row['Value']:,.0f}" if isinstance(row['Value'], (int, float)) else str(row['Value'])
                    st.write(f"{medal} {row['Dataset']}: {value}")

# Individual dataset tabs
for i, dataset in enumerate(datasets_available, 1):
    with tabs[i]:
        st.markdown(f'<div class="dataset-header">📁 {dataset} Analysis</div>', unsafe_allow_html=True)
        
        data = all_datasets[dataset]
        summary = data["summary"]

        # Key Metrics Row - Modern Cards
        st.subheader("📈 Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            unique_users = safe_get(summary, 'unique_real_users', 0)
            st.markdown(f'''
            <div class="metric-card">
                <h3 style="margin:0; color: #2c3e50;">👥 Unique Users</h3>
                <p style="font-size: 2rem; font-weight: bold; color: #3498db; margin:0;">{unique_users:,}</p>
                <p style="margin:0; color: #7f8c8d;">Real users after reconciliation</p>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            author_sets = safe_get(summary, 'unique_author_sets', 'N/A')
            st.markdown(f'''
            <div class="metric-card">
                <h3 style="margin:0; color: #2c3e50;">📚 Author Sets</h3>
                <p style="font-size: 2rem; font-weight: bold; color: #e74c3c; margin:0;">{author_sets}</p>
                <p style="margin:0; color: #7f8c8d;">Unique author combinations</p>
            </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            # Get top revenue author instead of just frequency
            top_revenue_authors = summary.get("top_revenue_authors", [])
            if top_revenue_authors and len(top_revenue_authors) > 0:
                display_author = top_revenue_authors[0].get('author', 'No data')
                revenue = safe_get(top_revenue_authors[0], 'revenue', 0)
                st.markdown(f'''
                <div class="metric-card">
                    <h3 style="margin:0; color: #2c3e50;">🏆 Top Revenue Author</h3>
                    <p style="font-size: 1.1rem; font-weight: bold; color: #27ae60; margin:0;">{display_author}</p>
                    <p style="font-size: 1rem; margin:0; color: #7f8c8d;">${revenue:,.2f} generated</p>
                </div>
                ''', unsafe_allow_html=True)
            else:
                popular_authors = summary.get("most_popular_authors", [])
                display_author = popular_authors[0] if popular_authors else "No data"
                st.markdown(f'''
                <div class="metric-card">
                    <h3 style="margin:0; color: #2c3e50;">🏆 Popular Author</h3>
                    <p style="font-size: 1.2rem; font-weight: bold; color: #27ae60; margin:0;">{display_author}</p>
                    <p style="margin:0; color: #7f8c8d;">Most frequent in catalog</p>
                </div>
                ''', unsafe_allow_html=True)
        
        with col4:
            total_spent = safe_get(summary, 'top_customer_total_spent', 0)
            st.markdown(f'''
            <div class="metric-card">
                <h3 style="margin:0; color: #2c3e50;">💰 Top Customer</h3>
                <p style="font-size: 1.5rem; font-weight: bold; color: #f39c12; margin:0;">${total_spent:,.2f}</p>
                <p style="margin:0; color: #7f8c8d;">Total spending</p>
            </div>
            ''', unsafe_allow_html=True)

        # Two-column layout for details
        col_left, col_right = st.columns(2)

        with col_left:
            # Top 5 Revenue Days
            st.subheader("🎯 Top 5 Revenue Days")
            top5_days = summary.get("top5_days", [])
            if top5_days:
                for i, day in enumerate(top5_days[:5], 1):
                    date = day.get('date', 'Unknown')
                    revenue = safe_get(day, 'paid_price', 0)
                    st.markdown(f'''
                    <div class="top-day-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="font-size: 1.1em;">#{i} {date}</strong>
                            </div>
                            <div style="font-size: 1.2em; font-weight: bold;">
                                ${revenue:,.2f}
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.info("No revenue day data available")

            # Best Buyer Information
            st.subheader("👑 Best Buyer Details")
            buyer_ids = summary.get("top_customer_user_ids", [])
            if buyer_ids:
                st.markdown(f'''
                <div class="customer-card">
                    <h4 style="margin:0;">User IDs</h4>
                    <p style="font-size: 1.1em; margin:0.5rem 0;">{', '.join(map(str, buyer_ids))}</p>
                    <h4 style="margin:0;">Total Spent</h4>
                    <p style="font-size: 1.3em; font-weight: bold; margin:0;">${total_spent:,.2f}</p>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.info("No buyer data available")

        with col_right:
            # Author Information
            st.subheader("📖 Author Revenue Analysis")
            unique_sets = safe_get(summary, 'unique_author_sets', 'N/A')
            st.markdown(f'''
            <div class="author-card">
                <h4 style="margin:0;">Unique Author Sets</h4>
                <p style="font-size: 2em; font-weight: bold; margin:0.5rem 0;">{unique_sets}</p>
                <p style="margin:0;">Different author combinations in catalog</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Show top revenue authors if available
            top_revenue_authors = summary.get("top_revenue_authors", [])
            if top_revenue_authors:
                st.subheader("💰 Top Revenue Authors")
                for author_data in top_revenue_authors[:5]:
                    author = author_data.get('author', 'Unknown')
                    revenue = safe_get(author_data, 'revenue', 0)
                    st.markdown(f"• **{author}**: ${revenue:,.2f}")
            else:
                # Fallback to frequency-based authors
                popular_authors = summary.get("most_popular_authors", [])
                if popular_authors:
                    st.subheader("🌟 Most Popular Authors")
                    for author in popular_authors[:5]:
                        st.markdown(f"• **{author}**")
                else:
                    st.info("No author data available")
            
            # Show author sets if available
            popular_sets = summary.get("most_popular_author_sets", [])
            if popular_sets and popular_sets[0]:
                st.subheader("👥 Most Popular Author Sets")
                for author_set in popular_sets[:3]:
                    st.markdown(f"**Set:** {', '.join(author_set)}")

        # Revenue Chart (full width)
        if data["revenue_data"] is not None and not data["revenue_data"].empty:
            st.markdown("---")
            st.subheader("📊 Revenue Analytics")
            
            df = data["revenue_data"].copy()
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date', 'paid_price'])
            
            if not df.empty:
                # Create interactive Plotly chart with modern styling
                fig = px.area(df, x='date', y='paid_price', 
                             title=f'📈 Daily Revenue Trend - {dataset}',
                             labels={'paid_price': 'Revenue (USD $)', 'date': 'Date'})
                
                # Customize the chart
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#2c3e50"),
                    height=400,
                    hovermode='x unified',
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='lightgray',
                        title_font=dict(size=14)
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='lightgray',
                        title_font=dict(size=14)
                    )
                )
                
                # Add styling to the area
                fig.update_traces(
                    line=dict(color='#3498db', width=3),
                    fillcolor='rgba(52, 152, 219, 0.3)',
                    hovertemplate='<b>%{x}</b><br>$%{y:,.2f}<extra></extra>'
                )
                
                st.plotly_chart(fig, use_container_width=True)

                # Revenue statistics in modern cards
                st.subheader("💹 Revenue Statistics")
                col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
                
                with col_stats1:
                    total_rev = df['paid_price'].sum()
                    st.markdown(f'''
                    <div class="metric-card">
                        <h4 style="margin:0; color: #2c3e50;">Total Revenue</h4>
                        <p style="font-size: 1.5rem; font-weight: bold; color: #27ae60; margin:0;">${total_rev:,.0f}</p>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col_stats2:
                    avg_daily = df['paid_price'].mean()
                    st.markdown(f'''
                    <div class="metric-card">
                        <h4 style="margin:0; color: #2c3e50;">Average Daily</h4>
                        <p style="font-size: 1.5rem; font-weight: bold; color: #3498db; margin:0;">${avg_daily:,.0f}</p>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col_stats3:
                    highest_day = df['paid_price'].max()
                    st.markdown(f'''
                    <div class="metric-card">
                        <h4 style="margin:0; color: #2c3e50;">Highest Day</h4>
                        <p style="font-size: 1.5rem; font-weight: bold; color: #e74c3c; margin:0;">${highest_day:,.0f}</p>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col_stats4:
                    days_count = len(df)
                    st.markdown(f'''
                    <div class="metric-card">
                        <h4 style="margin:0; color: #2c3e50;">Days Tracked</h4>
                        <p style="font-size: 1.5rem; font-weight: bold; color: #f39c12; margin:0;">{days_count}</p>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.info("No valid revenue data available for visualization")
        else:
            st.info("No revenue data available for visualization")

        # Download section
        st.markdown("---")
        st.subheader("📥 Data Export")
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            summary_file = os.path.join(OUTPUT_DIR, f"{dataset}_summary.json")
            if os.path.exists(summary_file):
                with open(summary_file, "r", encoding="utf-8") as f:
                    json_data = f.read()
                st.download_button(
                    label="📄 Download Summary JSON",
                    data=json_data,
                    file_name=f"{dataset}_summary.json",
                    mime="application/json",
                    use_container_width=True,
                    key=f"download_json_{dataset}"
                )
        
        with col_dl2:
            revenue_file = os.path.join(OUTPUT_DIR, f"{dataset}_daily_revenue.csv")
            if os.path.exists(revenue_file):
                with open(revenue_file, "r", encoding="utf-8") as f:
                    csv_data = f.read()
                st.download_button(
                    label="📊 Download Revenue CSV",
                    data=csv_data,
                    file_name=f"{dataset}_revenue.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key=f"download_csv_{dataset}"
                )

# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 2rem 0;">
    <h4 style="color: #2c3e50; margin-bottom: 1rem;">📈 Advanced Analytics Insights</h4>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
        <div style="padding: 1rem; background: #f8f9fa; border-radius: 10px;">
            <strong>🎯 Multi-Dataset Comparison</strong>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Compare performance across all datasets with unified metrics</p>
        </div>
        <div style="padding: 1rem; background: #f8f9fa; border-radius: 10px;">
            <strong>💰 Revenue-Optimized Insights</strong>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Authors ranked by revenue generation, not just frequency</p>
        </div>
        <div style="padding: 1rem; background: #f8f9fa; border-radius: 10px;">
            <strong>📊 Interactive Visualizations</strong>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Dynamic charts for comprehensive data exploration</p>
        </div>
    </div>
    <p style="margin: 0; font-size: 0.9rem;"><strong>Bookstore Analytics Platform</strong> • Real-time Business Intelligence • Data-Driven Decision Making</p>
</div>
""", unsafe_allow_html=True)
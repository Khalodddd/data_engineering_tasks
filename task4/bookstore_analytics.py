import os
import re
import json
import argparse
import math
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import subprocess
import sys

def install_dependencies():
    """Install required packages automatically"""
    required_packages = ['pandas', 'plotly', 'pyyaml', 'pyarrow', 'streamlit']
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install dependencies first
install_dependencies()

# Now import the installed packages
import yaml
from collections import defaultdict

class DataProcessor:
    def __init__(self, eur_rate=1.2):
        self.eur_rate = eur_rate
    
    def read_parquet_with_hint(self, path):
        try:
            return pd.read_parquet(path)
        except Exception as e:
            msg = str(e)
            if "pyarrow" in msg or "fastparquet" in msg or "parquet" in msg.lower():
                raise ImportError(
                    "Reading parquet failed. Install a parquet engine locally (pyarrow):\n"
                    "  pip install pyarrow\n\n"
                    f"Original error: {e}"
                )
            raise

    def read_yaml_list(self, path):
        with open(path, "r", encoding="utf-8") as f:
            obj = yaml.safe_load(f)
        if isinstance(obj, list):
            return obj
        if isinstance(obj, dict) and "books" in obj and isinstance(obj["books"], list):
            return obj["books"]
        if isinstance(obj, dict):
            vals = list(obj.values())
            if all(isinstance(v, dict) for v in vals):
                return vals
        return []

    def normalize_price_to_float(self, val):
        if pd.isna(val):
            return float("nan")
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip()
        if s == "":
            return float("nan")
        is_euro = "€" in s or "eur" in s.lower()
        s_clean = re.sub(r"[^\d\.\,\-]", "", s)
        if s_clean.count(",") == 1 and s_clean.count(".") == 0:
            s_clean = s_clean.replace(",", ".")
        s_clean = s_clean.replace(",", "")
        try:
            v = float(s_clean)
        except:
            v = float("nan")
        if is_euro and not math.isnan(v):
            v = v * self.eur_rate
        return v

    def clean_timestamp_str(self, s):
        if pd.isna(s):
            return s
        if not isinstance(s, str):
            return s
        t = s.strip()
        t = re.sub(r"\bA\.?M\.?\b", "AM", t, flags=re.IGNORECASE)
        t = re.sub(r"\bP\.?M\.?\b", "PM", t, flags=re.IGNORECASE)
        t = re.sub(r"\bM\.$", "", t)
        t = t.replace(",", " ")
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def parse_timestamp_series(self, srs):
        s_clean = srs.astype(object).apply(self.clean_timestamp_str)
        parsed = pd.to_datetime(s_clean, errors="coerce", dayfirst=False)
        return parsed

    class UnionFind:
        def __init__(self):
            self.parent = {}
        def find(self, x):
            if x not in self.parent:
                self.parent[x] = x
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]
        def union(self, a, b):
            ra, rb = self.find(a), self.find(b)
            if ra == rb:
                return
            self.parent[rb] = ra

    def reconcile_users(self, df_users):
        df = df_users.copy().fillna("").astype(str)
        if 'user_id' not in df.columns:
            if 'id' in df.columns:
                df = df.rename(columns={'id': 'user_id'})
            else:
                df = df.reset_index().rename(columns={'index': 'user_id'})
        for c in ['name','email','phone','address']:
            if c not in df.columns:
                df[c] = ''
        ids = df['user_id'].tolist()
        records = df[['name','email','phone','address']].map(lambda x: str(x).strip().lower()).to_dict(orient='records')
        uf = self.UnionFind()
        n = len(ids)
        for i in range(n):
            for j in range(i+1, n):
                matches = 0
                for k in ['name','email','phone','address']:
                    if records[i][k] != '' and records[i][k] == records[j][k]:
                        matches += 1
                if matches >= 3:
                    uf.union(ids[i], ids[j])
        mapping = {}
        clusters = defaultdict(list)
        for uid in ids:
            root = uf.find(uid)
            mapping[uid] = root
            clusters[root].append(uid)
        df['cluster_id'] = df['user_id'].map(mapping)
        return df, mapping, clusters

    def pick_col(self, cols, candidates):
        for c in candidates:
            if c in cols: return c
        lower = {col.lower(): col for col in cols}
        for c in candidates:
            if c.lower() in lower:
                return lower[c.lower()]
        return None

    def extract_authors_from_book(self, book):
        author_fields = [':author', 'author', 'authors', 'writer', 'writers']
        
        for field in author_fields:
            if field in book:
                authors_data = book[field]
                if isinstance(authors_data, str):
                    if ',' in authors_data:
                        return [a.strip() for a in authors_data.split(',') if a.strip()]
                    elif '&' in authors_data:
                        return [a.strip() for a in authors_data.split('&') if a.strip()]
                    elif ';' in authors_data:
                        return [a.strip() for a in authors_data.split(';') if a.strip()]
                    else:
                        return [authors_data.strip()]
                elif isinstance(authors_data, list):
                    return [str(a).strip() for a in authors_data if str(a).strip()]
                elif authors_data:
                    return [str(authors_data).strip()]
        
        for key, value in book.items():
            if 'author' in key.lower() and isinstance(value, str):
                return [value.strip()]
        
        return ['Unknown Author']

    def create_sample_data(self, data_dir):
        """Create sample data if none exists"""
        os.makedirs(data_dir, exist_ok=True)
        
        # Create sample users.csv
        users_data = """user_id,name,email,phone,address
1,John Doe,john@email.com,123-456-7890,123 Main St
2,Jane Smith,jane@email.com,098-765-4321,456 Oak Ave
3,John Doe,john.doe@email.com,123-456-7890,123 Main Street
4,Bob Wilson,bob@email.com,555-123-4567,789 Pine Rd"""
        
        with open(os.path.join(data_dir, 'users.csv'), 'w') as f:
            f.write(users_data)
        
        # Create sample orders.parquet
        orders_data = pd.DataFrame({
            'user_id': ['1', '2', '1', '3', '4', '2'],
            'book_id': ['B001', 'B002', 'B003', 'B001', 'B004', 'B005'],
            'quantity': [2, 1, 1, 3, 2, 1],
            'unit_price': ['$10.99', '€15.50', '$12.99', '$10.99', '€8.75', '$20.00'],
            'timestamp_raw': ['2024-01-15 10:30:00', '2024-01-16 14:45:00', 
                            '2024-01-17 09:15:00', '2024-01-18 16:20:00',
                            '2024-01-19 11:00:00', '2024-01-20 13:30:00']
        })
        orders_data.to_parquet(os.path.join(data_dir, 'orders.parquet'), index=False)
        
        # Create sample books.yaml
        books_data = """
- book_id: B001
  title: "The Great Novel"
  author: "John Author"
  price: 10.99
- book_id: B002
  title: "Science Fundamentals"
  author: "Jane Writer"
  price: 15.50
- book_id: B003
  title: "History of Everything"
  authors: ["Bob Historian", "Alice Researcher"]
  price: 12.99
- book_id: B004
  title: "Cooking Basics"
  author: "Chef Charlie"
  price: 8.75
- book_id: B005
  title: "Advanced Programming"
  author: "Dr. Developer"
  price: 20.00
"""
        with open(os.path.join(data_dir, 'books.yaml'), 'w') as f:
            f.write(books_data)
        
        print(f"✅ Created sample data in {data_dir}")

    def process_dataset_folder(self, data_dir, out_dir):
        dataset_name = os.path.basename(os.path.normpath(data_dir))
        print(f"\nProcessing dataset: {dataset_name}")
        os.makedirs(out_dir, exist_ok=True)

        users_path = os.path.join(data_dir, 'users.csv')
        orders_path = os.path.join(data_dir, 'orders.parquet')
        books_path = os.path.join(data_dir, 'books.yaml')

        # Create sample data if files don't exist
        if not all(os.path.exists(p) for p in [users_path, orders_path, books_path]):
            print(f"📝 Creating sample data for {dataset_name}...")
            self.create_sample_data(data_dir)

        df_users = pd.read_csv(users_path, dtype=str)
        df_orders = self.read_parquet_with_hint(orders_path)
        books_list = self.read_yaml_list(books_path)
        
        for book in books_list:
            book['authors'] = self.extract_authors_from_book(book)
        
        df_books = pd.DataFrame(books_list)

        print(f" users: {df_users.shape}")
        print(f" orders: {df_orders.shape}")
        print(f" books: {df_books.shape}")

        # Normalize orders columns
        ord_cols = df_orders.columns.tolist()
        user_col = self.pick_col(ord_cols, ['user_id','user','customer_id','customer','userId','id'])
        qty_col = self.pick_col(ord_cols, ['quantity','qty','count'])
        price_col = self.pick_col(ord_cols, ['unit_price','price','unitprice','amount'])
        ts_col = self.pick_col(ord_cols, ['timestamp','order_ts','created_at','order_date','date','time'])
        book_col = self.pick_col(ord_cols, ['book_id','isbn','sku','product_id','book'])

        rename_map = {}
        if user_col and user_col != 'user_id': rename_map[user_col] = 'user_id'
        if qty_col and qty_col != 'quantity': rename_map[qty_col] = 'quantity'
        if price_col and price_col != 'unit_price': rename_map[price_col] = 'unit_price'
        if ts_col and ts_col != 'timestamp_raw': rename_map[ts_col] = 'timestamp_raw'
        if book_col and book_col != 'book_id': rename_map[book_col] = 'book_id'
        if rename_map:
            df_orders = df_orders.rename(columns=rename_map)

        if 'quantity' not in df_orders.columns:
            df_orders['quantity'] = 1
        else:
            df_orders['quantity'] = pd.to_numeric(df_orders['quantity'], errors='coerce').fillna(0).astype(int)

        if 'unit_price' in df_orders.columns:
            df_orders['unit_price_clean'] = df_orders['unit_price'].apply(self.normalize_price_to_float)
        else:
            df_orders['unit_price_clean'] = 0.0

        df_orders['unit_price_usd'] = df_orders['unit_price_clean']
        df_orders['paid_price'] = df_orders['quantity'] * df_orders['unit_price_usd']
        df_orders['paid_price'] = pd.to_numeric(df_orders['paid_price'], errors='coerce').fillna(0.0).round(2)

        if 'timestamp_raw' in df_orders.columns:
            df_orders['timestamp_parsed'] = self.parse_timestamp_series(df_orders['timestamp_raw'])
        else:
            df_orders['timestamp_parsed'] = pd.NaT

        df_orders['date'] = df_orders['timestamp_parsed'].dt.date
        df_orders['year'] = df_orders['timestamp_parsed'].dt.year
        df_orders['month'] = df_orders['timestamp_parsed'].dt.month
        df_orders['day'] = df_orders['timestamp_parsed'].dt.day

        df_users_proc, mapping, clusters = self.reconcile_users(df_users)

        if 'user_id' in df_orders.columns:
            df_orders['user_id'] = df_orders['user_id'].astype(str)
            df_orders['cluster_id'] = df_orders['user_id'].map(mapping).fillna(df_orders['user_id'])
        else:
            df_orders['cluster_id'] = None

        book_cols = df_books.columns.tolist()
        book_id_books = self.pick_col(book_cols, ['book_id','id','isbn','sku'])
        if book_id_books and book_id_books != 'book_id':
            df_books = df_books.rename(columns={book_id_books: 'book_id'})
        if 'book_id' in df_books.columns:
            df_books['book_id'] = df_books['book_id'].astype(str)

        if 'book_id' in df_orders.columns and 'book_id' in df_books.columns:
            df_orders['book_id'] = df_orders['book_id'].astype(str)
            df_orders = df_orders.merge(df_books[['book_id','authors']], on='book_id', how='left')
        else:
            df_orders['authors'] = [[] for _ in range(len(df_orders))]

        df_orders['author_set'] = df_orders['authors'].apply(lambda a: tuple(sorted(a)) if isinstance(a, list) and a else ())

        daily_rev = df_orders.groupby('date', dropna=False)['paid_price'].sum().reset_index().sort_values('date')

        top5 = daily_rev.sort_values('paid_price', ascending=False).head(5).copy()
        top5['date'] = pd.to_datetime(top5['date'], errors='coerce').dt.strftime('%Y-%m-%d')
        top5_records = top5.to_dict(orient='records')

        unique_real_users = len(clusters)
        
        all_author_sets = set()
        for authors in df_books['authors']:
            if authors and isinstance(authors, list):
                all_author_sets.add(tuple(sorted(authors)))
        unique_author_sets = len(all_author_sets)

        author_frequency = defaultdict(int)
        for authors in df_books['authors']:
            if authors and isinstance(authors, list):
                for author in authors:
                    if author and author != 'Unknown Author':
                        author_frequency[author] += 1
        
        most_popular_authors = []
        if author_frequency:
            max_freq = max(author_frequency.values())
            most_popular_authors = [author for author, freq in author_frequency.items() if freq == max_freq]
        
        if not most_popular_authors and len(df_books) > 0:
            first_book_authors = df_books.iloc[0]['authors']
            if first_book_authors and isinstance(first_book_authors, list) and first_book_authors:
                most_popular_authors = [first_book_authors[0]]

        author_set_sales = defaultdict(int)
        for _, row in df_orders.iterrows():
            quantity = int(row.get('quantity', 0) or 0)
            author_set = row.get('author_set', ())
            if author_set:
                author_set_sales[author_set] += quantity
        
        most_popular_sets = []
        if author_set_sales:
            max_set_sales = max(author_set_sales.values())
            most_popular_sets = [list(author_set) for author_set, sales in author_set_sales.items() if sales == max_set_sales]

        cust_spend = df_orders.groupby('cluster_id')['paid_price'].sum().reset_index().sort_values('paid_price', ascending=False)
        if not cust_spend.empty:
            top_cluster = cust_spend.iloc[0]['cluster_id']
            top_total = float(cust_spend.iloc[0]['paid_price'])
            top_customer_user_ids = clusters.get(top_cluster, [top_cluster])
        else:
            top_cluster = None
            top_total = 0.0
            top_customer_user_ids = []

        out_prefix = os.path.join(out_dir, f"{dataset_name}")
        df_orders.to_csv(out_prefix + "_orders_enriched.csv", index=False)
        df_users_proc.to_csv(out_prefix + "_users_reconciled.csv", index=False)
        df_books.to_csv(out_prefix + "_books_processed.csv", index=False)
        daily_rev.to_csv(out_prefix + "_daily_revenue.csv", index=False)
        pd.DataFrame(top5_records).to_csv(out_prefix + "_top5_days.csv", index=False)

        summary = {
            'dataset': dataset_name,
            'top5_days': top5_records,
            'unique_real_users': int(unique_real_users),
            'unique_author_sets': int(unique_author_sets),
            'most_popular_author_sets': most_popular_sets,
            'most_popular_authors': most_popular_authors,
            'top_customer_cluster_id': top_cluster,
            'top_customer_user_ids': top_customer_user_ids,
            'top_customer_total_spent': float(round(top_total,2)),
            'daily_rev_csv': out_prefix + "_daily_revenue.csv",
            'orders_enriched_csv': out_prefix + "_orders_enriched.csv",
            'users_reconciled_csv': out_prefix + "_users_reconciled.csv",
            'books_processed_csv': out_prefix + "_books_processed.csv",
        }
        with open(out_prefix + "_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"✅ Finished {dataset_name}: real_users={unique_real_users}, author_sets={unique_author_sets}")
        return summary

    def process_all_data(self, data_root='./data', out_dir='./output'):
        """Process all datasets with automatic sample data creation"""
        if not os.path.exists(data_root):
            os.makedirs(data_root)
            print(f"📁 Created data directory: {data_root}")

        datasets = []
        for entry in sorted(os.listdir(data_root)):
            p = os.path.join(data_root, entry)
            if os.path.isdir(p) and entry.lower().startswith('data'):
                datasets.append(p)
        
        if not datasets:
            if all(os.path.exists(os.path.join(data_root, fn)) for fn in ['users.csv','orders.parquet','books.yaml']):
                datasets = [data_root]
            else:
                print("📝 No datasets found. Creating sample dataset...")
                datasets = [data_root]
                self.create_sample_data(data_root)

        all_summaries = []
        for d in datasets:
            try:
                s = self.process_dataset_folder(d, out_dir)
                all_summaries.append(s)
            except Exception as e:
                print(f"❌ ERROR processing {d}: {e}")
                continue

        with open(os.path.join(out_dir, 'all_summaries.json'), 'w', encoding='utf-8') as f:
            json.dump(all_summaries, f, indent=2, ensure_ascii=False)
        
        print(f"✅ All datasets processed. Outputs saved to: {out_dir}")
        return all_summaries

class Dashboard:
    def __init__(self):
        self.processor = DataProcessor()
        self.output_dir = "./output"
        
    def ensure_data_exists(self):
        """Make sure data is processed before showing dashboard"""
        if not os.path.exists(self.output_dir) or not any(fname.endswith('_summary.json') for fname in os.listdir(self.output_dir)):
            st.info("🔄 First run: Processing data... This may take a moment.")
            with st.spinner("Processing bookstore data..."):
                self.processor.process_all_data()
            st.success("✅ Data processed successfully!")
    
    def setup_page(self):
        st.set_page_config(
            page_title="Bookstore Analytics Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
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
    
    def load_data(self):
        datasets = {}
        for dataset in ["DATA1", "DATA2", "DATA3"]:
            summary_file = os.path.join(self.output_dir, f"{dataset}_summary.json")
            revenue_file = os.path.join(self.output_dir, f"{dataset}_daily_revenue.csv")
            
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
        
        return datasets
    
    def render_dashboard(self):
        self.setup_page()
        
        st.markdown('<h1 class="main-header">📊 Bookstore Analytics Dashboard</h1>', unsafe_allow_html=True)
        
        # Ensure data exists
        self.ensure_data_exists()
        
        # Load data
        datasets = self.load_data()
        
        if not datasets:
            st.error("❌ No datasets available. Please check data processing.")
            return
        
        st.success(f"✅ {len(datasets)} dataset(s) loaded successfully!")
        
        # Create tabs
        tab_names = ["📊 COMPARISON DASHBOARD"] + [f"📁 {dataset}" for dataset in datasets.keys()]
        tabs = st.tabs(tab_names)
        
        # Comparison Tab
        with tabs[0]:
            st.markdown("## 📈 Multi-Dataset Performance Overview")
            
            # KPI Cards
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
        
        # Individual Dataset Tabs
        for i, (dataset, data) in enumerate(datasets.items(), 1):
            with tabs[i]:
                summary = data["summary"]
                
                st.markdown(f"## 📋 {dataset} - Detailed Analysis")
                
                # Key Metrics
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
                
                # Two Column Layout
                col_left, col_right = st.columns(2)
                
                with col_left:
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
                
                # Revenue Chart
                if data["revenue_data"] is not None and not data["revenue_data"].empty:
                    st.markdown("### 📈 Revenue Analytics")
                    
                    df = data["revenue_data"].copy()
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    df = df.dropna(subset=['date', 'paid_price'])
                    
                    if not df.empty:
                        fig = px.area(df, x='date', y='paid_price', 
                                    title=f"{dataset} - Daily Revenue Trend",
                                    labels={'paid_price': 'Revenue ($)', 'date': 'Date'})
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color="#2c3e50"),
                            height=400,
                            hovermode='x unified'
                        )
                        
                        fig.update_traces(
                            line=dict(color='#3498db', width=3),
                            fillcolor='rgba(52, 152, 219, 0.3)'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("📊 No valid revenue data for visualization")
                else:
                    st.info("📊 No revenue chart data available")
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #7f8c8d; padding: 2rem 0;">
            <p><strong>Bookstore Analytics Platform</strong> • Business Intelligence Dashboard</p>
            <p>Data Sources: orders.parquet, books.yaml, users.csv • Processed with Python</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main function to run the application"""
    dashboard = Dashboard()
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()
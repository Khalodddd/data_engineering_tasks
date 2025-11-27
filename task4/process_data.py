import os
import re
import json
import argparse
import math
from collections import defaultdict
import pandas as pd

def read_parquet_with_hint(path):
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

def read_yaml_list(path):
    import yaml
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

def normalize_price_to_float(val, eur_to_usd=1.2):
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
        v = v * eur_to_usd
    return v

def clean_timestamp_str(s):
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

def parse_timestamp_series(srs):
    s_clean = srs.astype(object).apply(clean_timestamp_str)
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

def reconcile_users(df_users):
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
    uf = UnionFind()
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

def pick_col(cols, candidates):
    for c in candidates:
        if c in cols: return c
    lower = {col.lower(): col for col in cols}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    return None

def extract_authors_from_book(book):
    """Extract authors from book data - handle different field names and formats"""
    # Try different possible author field names
    author_fields = [':author', 'author', 'authors', 'writer', 'writers']
    
    for field in author_fields:
        if field in book:
            authors_data = book[field]
            if isinstance(authors_data, str):
                # Handle string formats
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
    
    # If no author field found, try to extract from other fields
    for key, value in book.items():
        if 'author' in key.lower() and isinstance(value, str):
            return [value.strip()]
    
    return ['Unknown Author']

def process_dataset_folder(data_dir, out_dir, eur_rate=1.2):
    dataset_name = os.path.basename(os.path.normpath(data_dir))
    print(f"\nProcessing dataset: {dataset_name}")
    os.makedirs(out_dir, exist_ok=True)

    users_path = os.path.join(data_dir, 'users.csv')
    orders_path = os.path.join(data_dir, 'orders.parquet')
    books_path = os.path.join(data_dir, 'books.yaml')

    if not os.path.exists(users_path) or not os.path.exists(orders_path) or not os.path.exists(books_path):
        raise FileNotFoundError(f"Dataset {dataset_name} missing one of users.csv / orders.parquet / books.yaml")

    df_users = pd.read_csv(users_path, dtype=str)
    df_orders = read_parquet_with_hint(orders_path)
    books_list = read_yaml_list(books_path)
    
    # Extract authors properly
    for book in books_list:
        book['authors'] = extract_authors_from_book(book)
    
    df_books = pd.DataFrame(books_list)

    print(f" users: {df_users.shape}")
    print(f" orders: {df_orders.shape}")
    print(f" books: {df_books.shape}")
    print(f" sample authors: {[book.get('authors', []) for book in books_list[:3]]}")

    # normalize orders columns
    ord_cols = df_orders.columns.tolist()
    user_col = pick_col(ord_cols, ['user_id','user','customer_id','customer','userId','id'])
    qty_col = pick_col(ord_cols, ['quantity','qty','count'])
    price_col = pick_col(ord_cols, ['unit_price','price','unitprice','amount'])
    ts_col = pick_col(ord_cols, ['timestamp','order_ts','created_at','order_date','date','time'])
    book_col = pick_col(ord_cols, ['book_id','isbn','sku','product_id','book'])

    rename_map = {}
    if user_col and user_col != 'user_id': rename_map[user_col] = 'user_id'
    if qty_col and qty_col != 'quantity': rename_map[qty_col] = 'quantity'
    if price_col and price_col != 'unit_price': rename_map[price_col] = 'unit_price'
    if ts_col and ts_col != 'timestamp_raw': rename_map[ts_col] = 'timestamp_raw'
    if book_col and book_col != 'book_id': rename_map[book_col] = 'book_id'
    if rename_map:
        df_orders = df_orders.rename(columns=rename_map)

    # ensure numeric quantity
    if 'quantity' not in df_orders.columns:
        df_orders['quantity'] = 1
    else:
        df_orders['quantity'] = pd.to_numeric(df_orders['quantity'], errors='coerce').fillna(0).astype(int)

    # price normalization
    if 'unit_price' in df_orders.columns:
        df_orders['unit_price_clean'] = df_orders['unit_price'].apply(lambda v: normalize_price_to_float(v, eur_rate))
    else:
        df_orders['unit_price_clean'] = 0.0

    df_orders['unit_price_usd'] = df_orders['unit_price_clean']
    df_orders['paid_price'] = df_orders['quantity'] * df_orders['unit_price_usd']
    df_orders['paid_price'] = pd.to_numeric(df_orders['paid_price'], errors='coerce').fillna(0.0).round(2)

    # timestamps
    if 'timestamp_raw' in df_orders.columns:
        df_orders['timestamp_parsed'] = parse_timestamp_series(df_orders['timestamp_raw'])
    else:
        df_orders['timestamp_parsed'] = pd.NaT

    df_orders['date'] = df_orders['timestamp_parsed'].dt.date
    df_orders['year'] = df_orders['timestamp_parsed'].dt.year
    df_orders['month'] = df_orders['timestamp_parsed'].dt.month
    df_orders['day'] = df_orders['timestamp_parsed'].dt.day

    # users reconciliation
    df_users_proc, mapping, clusters = reconcile_users(df_users)

    if 'user_id' in df_orders.columns:
        df_orders['user_id'] = df_orders['user_id'].astype(str)
        df_orders['cluster_id'] = df_orders['user_id'].map(mapping).fillna(df_orders['user_id'])
    else:
        df_orders['cluster_id'] = None

    # prepare books/authors
    book_cols = df_books.columns.tolist()
    book_id_books = pick_col(book_cols, ['book_id','id','isbn','sku'])
    if book_id_books and book_id_books != 'book_id':
        df_books = df_books.rename(columns={book_id_books: 'book_id'})
    if 'book_id' in df_books.columns:
        df_books['book_id'] = df_books['book_id'].astype(str)

    # join orders with books to get authors
    if 'book_id' in df_orders.columns and 'book_id' in df_books.columns:
        df_orders['book_id'] = df_orders['book_id'].astype(str)
        df_orders = df_orders.merge(df_books[['book_id','authors']], on='book_id', how='left')
    else:
        df_orders['authors'] = [[] for _ in range(len(df_orders))]

    df_orders['author_set'] = df_orders['authors'].apply(lambda a: tuple(sorted(a)) if isinstance(a, list) and a else ())

    # daily revenue
    daily_rev = df_orders.groupby('date', dropna=False)['paid_price'].sum().reset_index().sort_values('date')

    # top 5 days
    top5 = daily_rev.sort_values('paid_price', ascending=False).head(5).copy()
    top5['date'] = pd.to_datetime(top5['date'], errors='coerce').dt.strftime('%Y-%m-%d')
    top5_records = top5.to_dict(orient='records')

    unique_real_users = len(clusters)
    
    # Count unique author sets properly
    all_author_sets = set()
    for authors in df_books['authors']:
        if authors and isinstance(authors, list):
            all_author_sets.add(tuple(sorted(authors)))
    unique_author_sets = len(all_author_sets)

    # most popular author(s) - simplified approach
    # Count author frequency in books data first
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
        print(f"Most frequent authors: {most_popular_authors} (appears {max_freq} times)")
    
    # If that doesn't work, just get the first author from the first book
    if not most_popular_authors and len(df_books) > 0:
        first_book_authors = df_books.iloc[0]['authors']
        if first_book_authors and isinstance(first_book_authors, list) and first_book_authors:
            most_popular_authors = [first_book_authors[0]]
            print(f"Using first author: {most_popular_authors}")

    # most popular author sets
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

    # top customer by cluster spending
    cust_spend = df_orders.groupby('cluster_id')['paid_price'].sum().reset_index().sort_values('paid_price', ascending=False)
    if not cust_spend.empty:
        top_cluster = cust_spend.iloc[0]['cluster_id']
        top_total = float(cust_spend.iloc[0]['paid_price'])
        top_customer_user_ids = clusters.get(top_cluster, [top_cluster])
    else:
        top_cluster = None
        top_total = 0.0
        top_customer_user_ids = []

    # save outputs
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

    print(f"Finished {dataset_name}: real_users={unique_real_users}, author_sets={unique_author_sets}, popular_authors={most_popular_authors}")
    return summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-root', type=str, default='./data', help='root folder with DATA1/DATA2/DATA3')
    parser.add_argument('--out-dir', type=str, default='./output', help='output folder')
    parser.add_argument('--eur-rate', type=float, default=1.2, help='EUR -> USD conversion rate')
    args = parser.parse_args()

    data_root = args.data_root
    out_dir = args.out_dir
    eur_rate = args.eur_rate

    if not os.path.exists(data_root):
        raise FileNotFoundError(f"{data_root} not found")

    datasets = []
    for entry in sorted(os.listdir(data_root)):
        p = os.path.join(data_root, entry)
        if os.path.isdir(p) and entry.lower().startswith('data'):
            datasets.append(p)
    if not datasets:
        if all(os.path.exists(os.path.join(data_root, fn)) for fn in ['users.csv','orders.parquet','books.yaml']):
            datasets = [data_root]
        else:
            raise FileNotFoundError("No DATA* folders found and no direct dataset files found under data-root")

    all_summaries = []
    for d in datasets:
        try:
            s = process_dataset_folder(d, out_dir, eur_rate)
            all_summaries.append(s)
        except ImportError as e:
            print("ERROR:", e)
            print("Install parquet engine locally, e.g.: pip install pyarrow")
            return
        except Exception as e:
            print("ERROR processing", d, ":", e)
            continue

    with open(os.path.join(out_dir, 'all_summaries.json'), 'w', encoding='utf-8') as f:
        json.dump(all_summaries, f, indent=2, ensure_ascii=False)
    print("\nAll datasets processed. Outputs saved to:", out_dir)

if __name__ == "__main__":
    main()
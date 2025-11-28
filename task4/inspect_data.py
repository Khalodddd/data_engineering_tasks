import json

datasets = ['DATA1', 'DATA2', 'DATA3']

for dataset in datasets:
    print(f"\n=== {dataset} ===")
    try:
        with open(f'dashboard_data_{dataset}.json', 'r') as f:
            data = json.load(f)
        print(f"Users: {data['n_real_users']}")
        print(f"Author Sets: {data['n_author_sets']}")
        print(f"Top Author: {data['most_popular_author_set']}")
        print(f"Best Buyer: {data['best_buyer']}")
        print(f"Revenue data points: {len(data['daily_revenue'])}")
        if data['daily_revenue']:
            print(f"First revenue entry: {data['daily_revenue'][0]}")
    except Exception as e:
        print(f"Error: {e}")
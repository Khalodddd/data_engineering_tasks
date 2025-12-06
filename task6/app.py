from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_CONFIG = {
    'dbname': 'fake_user_data',
    'user': 'fake_user',
    'password': '20221311293',
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT locale_id, locale_name FROM locales ORDER BY locale_id")
    locales = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', locales=locales)

@app.route('/generate', methods=['POST'])
def generate_users():
    try:
        data = request.json
        locale = data.get('locale', 'en_US')
        seed = int(data.get('seed', 12345))
        batch_index = int(data.get('batch_index', 0))
        batch_size = int(data.get('batch_size', 10))
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT * FROM generate_users_batch(%s, %s, %s, %s)", 
                   (locale, seed, batch_index, batch_size))
        
        results = []
        for record in cur.fetchall():
            results.append(dict(record))
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'users': results,
            'batch_index': batch_index,
            'seed': seed,
            'total_generated': (batch_index + 1) * batch_size
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

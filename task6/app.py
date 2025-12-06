from flask import Flask, render_template, request, jsonify
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://')
        return psycopg2.connect(database_url, sslmode='require')
    else:
        return psycopg2.connect(
            dbname="fake_user_data",
            user="postgres",
            password="20221311293",
            host="localhost",
            port="5432"
        )

@app.route('/')
def index():
    locales = ['USA', 'Germany']
    return render_template('index.html', locales=locales)

@app.route('/generate', methods=['POST'])
def generate_users():
    try:
        data = request.get_json()
        locale = data.get('locale', 'USA')
        seed = data.get('seed', 12345)
        batch_size = data.get('batch_size', 10)
        batch_index = data.get('batch_index', 0)
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM generate_users_batch(%s, %s, %s, %s)", (locale, seed, batch_size, batch_index))
        users = cur.fetchall()
        
        results = []
        for row in users:
            results.append({
                'id': row[0], 'first_name': row[1], 'last_name': row[2],
                'email': row[3], 'phone': row[4], 'address': row[5],
                'latitude': row[6], 'longitude': row[7],
                'height_cm': row[8], 'weight_kg': row[9]
            })
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True, 'users': results, 'batch_index': batch_index,
            'seed': seed, 'total_generated': (batch_index + 1) * batch_size
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

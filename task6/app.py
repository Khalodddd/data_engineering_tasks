from flask import Flask, render_template, request, jsonify
import psycopg2

app = Flask(__name__)

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
        
        print(f"DEBUG: Generating - locale={locale}, seed={seed}, batch_size={batch_size}, batch_index={batch_index}")
        
        # Use password connection
        conn = psycopg2.connect(
            dbname="fake_user_data",
            user="postgres",
            password="20221311293",
            host="localhost",
            port="5432"
        )
        
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM generate_users_batch(%s, %s, %s, %s)", 
                   (locale, seed, batch_size, batch_index))
        users = cur.fetchall()
        
        print(f"DEBUG: Got {len(users)} users from database")
        
        # Convert to list of dictionaries
        results = []
        for row in users:
            results.append({
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'email': row[3],
                'phone': row[4],
                'address': row[5],
                'latitude': row[6],
                'longitude': row[7],
                'height_cm': row[8],
                'weight_kg': row[9]
            })
        
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
        print(f"ERROR in generate_users: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

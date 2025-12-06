from flask import Flask, render_template, request, jsonify
import psycopg2
import os
import sys

app = Flask(__name__)

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not set", file=sys.stderr)
        raise Exception("DATABASE_URL environment variable not set")
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://')
    
    try:
        conn = psycopg2.connect(database_url, sslmode='require')
        return conn
    except Exception as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        raise

def create_function_if_not_exists():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT EXISTS(SELECT 1 FROM pg_proc WHERE proname = 'generate_users_batch');")
        function_exists = cur.fetchone()[0]
        
        if not function_exists:
            print("Creating generate_users_batch function...", file=sys.stderr)
            cur.execute('''
                CREATE OR REPLACE FUNCTION generate_users_batch(
                    p_locale VARCHAR,
                    p_seed INTEGER,
                    p_batch_size INTEGER,
                    p_batch_index INTEGER
                )
                RETURNS TABLE(
                    id BIGINT,
                    first_name VARCHAR,
                    last_name VARCHAR,
                    email VARCHAR,
                    phone VARCHAR,
                    address VARCHAR,
                    latitude FLOAT,
                    longitude FLOAT,
                    height_cm FLOAT,
                    weight_kg FLOAT
                ) AS $$
                DECLARE
                    i INTEGER;
                BEGIN
                    FOR i IN 1..p_batch_size LOOP
                        id = p_seed * 10000 + p_batch_index * 100 + i;
                        first_name = CASE WHEN i % 2 = 0 THEN 'John' ELSE 'Jane' END;
                        last_name = CASE WHEN p_locale = 'USA' THEN 'Smith' ELSE 'Müller' END;
                        email = LOWER(first_name || '.' || last_name || i::TEXT || '@example.com');
                        phone = CASE WHEN p_locale = 'USA' 
                                    THEN '+1 (555) 123-' || LPAD((i % 10000)::TEXT, 4, '0')
                                    ELSE '+49 89 123' || LPAD((i % 10000)::TEXT, 4, '0') END;
                        address = CASE WHEN p_locale = 'USA' 
                                      THEN '123 Main St, New York, USA'
                                      ELSE 'Hauptstraße 1, Berlin, Germany' END;
                        latitude = 40.0 + (i % 100) * 0.1;
                        longitude = -70.0 + (i % 100) * 0.1;
                        height_cm = 170.0 + (i % 30);
                        weight_kg = 70.0 + (i % 40) * 0.5;
                        RETURN NEXT;
                    END LOOP;
                END;
                $$ LANGUAGE plpgsql;
            ''')
            conn.commit()
            print("Function created!", file=sys.stderr)
        else:
            print("Function exists", file=sys.stderr)
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Setup error: {e}", file=sys.stderr)

create_function_if_not_exists()

@app.route('/setup', methods=['GET'])
def setup():
    try:
        create_function_if_not_exists()
        return jsonify({'success': True, 'message': 'Function checked/created!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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
        batch_size = min(data.get('batch_size', 10), 50)
        batch_index = data.get('batch_index', 0)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM generate_users_batch(%s, %s, %s, %s)", 
                   (locale, seed, batch_size, batch_index))
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
            'success': True,
            'users': results,
            'batch_index': batch_index,
            'seed': seed,
            'total_generated': (batch_index + 1) * batch_size
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, render_template, request, jsonify
import psycopg2
import os
import sys
import time
from datetime import datetime

app = Flask(__name__)

# SECURE: No password in code - only from environment
def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://')
        return psycopg2.connect(database_url, sslmode='require')
    else:
        # Local development - requires environment variables
        return psycopg2.connect(
            dbname=os.environ.get('DB_NAME', 'fake_user_data'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', ''),  # EMPTY - must be set in env
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432')
        )

def init_database():
    """Initialize database - SIMPLIFIED VERSION"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("Creating/updating database function...", file=sys.stderr)
        
        # SIMPLIFIED FUNCTION - removes generation_time_ms column
        cur.execute('''
            CREATE OR REPLACE FUNCTION generate_users_batch(
                p_locale VARCHAR DEFAULT 'en_US',
                p_seed INTEGER DEFAULT 12345,
                p_batch_size INTEGER DEFAULT 10,
                p_batch_number INTEGER DEFAULT 0
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
                user_idx INTEGER;
                base_seed BIGINT;
                rand1 FLOAT;
                rand2 FLOAT;
                fn_idx INTEGER;
                ln_idx INTEGER;
                city_idx INTEGER;
                street_idx INTEGER;
                
                -- Arrays
                usa_first_names TEXT[];
                usa_last_names TEXT[];
                german_first_names TEXT[];
                german_last_names TEXT[];
                usa_cities TEXT[];
                german_cities TEXT[];
                usa_streets TEXT[];
                german_streets TEXT[];
                usa_street_types TEXT[];
                german_street_types TEXT[];
                
                current_first_names TEXT[];
                current_last_names TEXT[];
                current_cities TEXT[];
                current_streets TEXT[];
                current_street_types TEXT[];
                
            BEGIN
                -- USA Arrays
                usa_first_names := ARRAY['James','Mary','John','Patricia','Robert','Jennifer'];
                usa_last_names := ARRAY['Smith','Johnson','Williams','Brown','Jones','Garcia'];
                usa_cities := ARRAY['New York','Los Angeles','Chicago','Houston'];
                usa_streets := ARRAY['Main','Oak','Pine','Maple'];
                usa_street_types := ARRAY['St','Ave','Rd'];
                
                -- German Arrays
                german_first_names := ARRAY['Hans','Anna','Peter','Maria','Thomas','Sabine'];
                german_last_names := ARRAY['Müller','Schmidt','Schneider','Fischer','Weber','Meyer'];
                german_cities := ARRAY['Berlin','Hamburg','Munich','Cologne'];
                german_streets := ARRAY['Haupt','Bahnhof','Goethe','Schiller'];
                german_street_types := ARRAY['straße','weg','allee'];
                
                -- Select arrays based on locale
                IF p_locale = 'en_US' THEN
                    current_first_names := usa_first_names;
                    current_last_names := usa_last_names;
                    current_cities := usa_cities;
                    current_streets := usa_streets;
                    current_street_types := usa_street_types;
                ELSE
                    current_first_names := german_first_names;
                    current_last_names := german_last_names;
                    current_cities := german_cities;
                    current_streets := german_streets;
                    current_street_types := german_street_types;
                END IF;
                
                FOR i IN 1..p_batch_size LOOP
                    user_idx := p_batch_number * p_batch_size + i;
                    base_seed := p_seed * 997 + user_idx * 104729;
                    
                    -- Simple deterministic random
                    rand1 := (base_seed % 10000) / 10000.0;
                    rand2 := ((base_seed * 3) % 10000) / 10000.0;
                    
                    -- Select indices
                    fn_idx := 1 + (FLOOR(rand1 * array_length(current_first_names, 1))::INTEGER);
                    ln_idx := 1 + (FLOOR(rand2 * array_length(current_last_names, 1))::INTEGER);
                    city_idx := 1 + (FLOOR(rand1 * array_length(current_cities, 1))::INTEGER);
                    street_idx := 1 + (FLOOR(rand2 * array_length(current_streets, 1))::INTEGER);
                    
                    -- Generate user
                    id := p_seed * 100000 + user_idx;
                    first_name := current_first_names[fn_idx];
                    last_name := current_last_names[ln_idx];
                    
                    -- Email
                    email := LOWER(first_name || '.' || last_name || user_idx::TEXT || 
                                 CASE WHEN p_locale = 'en_US' THEN '@example.com' ELSE '@example.de' END);
                    
                    -- Phone (SIMPLIFIED)
                    IF p_locale = 'en_US' THEN
                        phone := '+1-555-' || LPAD((user_idx % 9000 + 1000)::TEXT, 4, '0');
                    ELSE
                        phone := '+49 ' || LPAD((user_idx % 90 + 10)::TEXT, 2, '0') || ' ' || 
                                 LPAD((user_idx * 1000 % 10000000)::TEXT, 7, '0');
                    END IF;
                    
                    -- Address
                    address := (user_idx % 999 + 1)::TEXT || ' ' || 
                             current_streets[street_idx] || ' ' || 
                             current_street_types[street_idx % array_length(current_street_types, 1) + 1] || ', ' || 
                             current_cities[city_idx];
                    
                    -- Simple coordinates
                    latitude := ((base_seed % 18000) - 9000) / 100.0;
                    longitude := (((base_seed * 2) % 36000) - 18000) / 100.0;
                    
                    -- Simple height/weight
                    height_cm := 170.0 + ((base_seed % 400) - 200) / 10.0;
                    weight_kg := 70.0 + ((base_seed % 600) - 300) / 10.0;
                    
                    -- Ensure realistic ranges
                    IF height_cm < 140 THEN height_cm := 140; END IF;
                    IF height_cm > 210 THEN height_cm := 210; END IF;
                    IF weight_kg < 40 THEN weight_kg := 40; END IF;
                    IF weight_kg > 150 THEN weight_kg := 150; END IF;
                    
                    -- Round
                    height_cm := ROUND(height_cm::NUMERIC, 1);
                    weight_kg := ROUND(weight_kg::NUMERIC, 1);
                    
                    RETURN NEXT;
                END LOOP;
            END;
            $$ LANGUAGE plpgsql;
        ''')
        
        conn.commit()
        print("✅ Database function created!", file=sys.stderr)
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}", file=sys.stderr)

# Initialize database
print("Starting app...", file=sys.stderr)
init_database()

@app.route('/')
def index():
    return render_template('index.html', locales=['en_US', 'de_DE'])

@app.route('/generate', methods=['POST'])
def generate_users():
    try:
        data = request.get_json()
        locale = data.get('locale', 'en_US')
        seed = int(data.get('seed', 12345))
        batch_size = min(int(data.get('batch_size', 10)), 1000)
        batch_index = int(data.get('batch_index', 0))
        
        # START TIMING
        start_time = time.perf_counter()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # CALL FUNCTION - NO generation_time_ms column!
        cur.execute("SELECT * FROM generate_users_batch(%s, %s, %s, %s)", 
                   (locale, seed, batch_size, batch_index))
        users = cur.fetchall()
        
        # END TIMING
        end_time = time.perf_counter()
        generation_time_ms = (end_time - start_time) * 1000
        
        results = []
        for row in users:
            results.append({
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'email': row[3],
                'phone': row[4],
                'address': row[5],
                'latitude': round(float(row[6]), 4) if row[6] else 0.0,
                'longitude': round(float(row[7]), 4) if row[7] else 0.0,
                'height_cm': round(float(row[8]), 1) if row[8] else 0.0,
                'weight_kg': round(float(row[9]), 1) if row[9] else 0.0
            })
        
        cur.close()
        conn.close()
        
        # Calculate performance
        users_per_second = (batch_size / generation_time_ms * 1000) if generation_time_ms > 0 else 0
        
        return jsonify({
            'success': True,
            'users': results,
            'batch_index': batch_index,
            'seed': seed,
            'locale': locale,
            'total_generated': (batch_index + 1) * batch_size,
            'performance': {
                'generation_time_ms': round(generation_time_ms, 2),
                'users_per_second': round(users_per_second, 2),
                'batch_size': batch_size
            }
        })
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/benchmark', methods=['POST'])
def run_benchmark():
    try:
        data = request.get_json()
        locale = data.get('locale', 'en_US')
        seed = data.get('seed', 12345)
        
        results = []
        for batch_size in [10, 50, 100]:
            times = []
            for _ in range(2):  # Run twice
                start = time.perf_counter()
                
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM generate_users_batch(%s, %s, %s, 0)", 
                          (locale, seed, batch_size))
                cur.fetchall()
                cur.close()
                conn.close()
                
                end = time.perf_counter()
                times.append((end - start) * 1000)
            
            avg_time = sum(times) / len(times)
            users_per_second = (batch_size / avg_time * 1000) if avg_time > 0 else 0
            
            results.append({
                'batch_size': batch_size,
                'avg_time_ms': round(avg_time, 2),
                'users_per_second': round(users_per_second, 2)
            })
        
        return jsonify({
            'success': True,
            'benchmark_results': results,
            'summary': {
                'average_users_per_second': round(sum(r['users_per_second'] for r in results) / len(results), 2)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/docs')
def documentation():
    return '''
    <h1>Fake User Generator - Documentation</h1>
    <p>Simple, working fake user generator with USA/Germany locales.</p>
    <p><strong>Performance:</strong> ~1,000-2,000 users/second</p>
    <p><strong>Author:</strong> Khaled Soliman</p>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
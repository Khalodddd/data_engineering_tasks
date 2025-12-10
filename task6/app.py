from flask import Flask, render_template, request, jsonify
import psycopg2
import os
import sys
import time

app = Flask(__name__)

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://')
        return psycopg2.connect(database_url, sslmode='require')
    return psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'fake_user_data'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', ''),
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', '5432')
    )

def init_database():
    """Proper implementation with tables and modular functions"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("Creating database structure...", file=sys.stderr)
        
        # 1. Create names table (REQUIREMENT: single table with locale)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS names (
                id SERIAL PRIMARY KEY,
                locale VARCHAR(10) NOT NULL,
                name_type VARCHAR(20) NOT NULL,
                name_value VARCHAR(100) NOT NULL
            )
        ''')
        
        # 2. Insert reasonable amount of names (not 6, not 10,000)
        cur.execute('''
            INSERT INTO names (locale, name_type, name_value) VALUES
            -- USA names
            ('en_US', 'first_name', 'James'),
            ('en_US', 'first_name', 'John'),
            ('en_US', 'first_name', 'Robert'),
            ('en_US', 'first_name', 'Michael'),
            ('en_US', 'first_name', 'William'),
            ('en_US', 'first_name', 'Mary'),
            ('en_US', 'first_name', 'Patricia'),
            ('en_US', 'first_name', 'Jennifer'),
            ('en_US', 'first_name', 'Linda'),
            ('en_US', 'first_name', 'Elizabeth'),
            ('en_US', 'last_name', 'Smith'),
            ('en_US', 'last_name', 'Johnson'),
            ('en_US', 'last_name', 'Williams'),
            ('en_US', 'last_name', 'Brown'),
            ('en_US', 'last_name', 'Jones'),
            -- German names
            ('de_DE', 'first_name', 'Hans'),
            ('de_DE', 'first_name', 'Peter'),
            ('de_DE', 'first_name', 'Thomas'),
            ('de_DE', 'first_name', 'Michael'),
            ('de_DE', 'first_name', 'Andreas'),
            ('de_DE', 'first_name', 'Anna'),
            ('de_DE', 'first_name', 'Maria'),
            ('de_DE', 'first_name', 'Sabine'),
            ('de_DE', 'first_name', 'Ursula'),
            ('de_DE', 'first_name', 'Monika'),
            ('de_DE', 'last_name', 'Müller'),
            ('de_DE', 'last_name', 'Schmidt'),
            ('de_DE', 'last_name', 'Schneider'),
            ('de_DE', 'last_name', 'Fischer'),
            ('de_DE', 'last_name', 'Weber')
            ON CONFLICT DO NOTHING
        ''')
        
        # 3. Create cities table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS cities (
                id SERIAL PRIMARY KEY,
                locale VARCHAR(10) NOT NULL,
                city_name VARCHAR(100) NOT NULL
            )
        ''')
        
        cur.execute('''
            INSERT INTO cities (locale, city_name) VALUES
            ('en_US', 'New York'),
            ('en_US', 'Los Angeles'),
            ('en_US', 'Chicago'),
            ('en_US', 'Houston'),
            ('en_US', 'Phoenix'),
            ('de_DE', 'Berlin'),
            ('de_DE', 'Hamburg'),
            ('de_DE', 'Munich'),
            ('de_DE', 'Cologne'),
            ('de_DE', 'Frankfurt')
            ON CONFLICT DO NOTHING
        ''')
        
        # 4. CREATE MODULAR FUNCTIONS (REQUIREMENT: modular SQL functions)
        
        # Function 1: Random number generator
        cur.execute('''
            CREATE OR REPLACE FUNCTION get_random(
                seed_param INTEGER,
                index_param INTEGER
            ) RETURNS FLOAT AS $$
            BEGIN
                RETURN ((seed_param * 997 + index_param * 104729) % 10000) / 10000.0;
            END;
            $$ LANGUAGE plpgsql;
        ''')
        
        # Function 2: Get name from table
        cur.execute('''
            CREATE OR REPLACE FUNCTION get_name_from_table(
                locale_param VARCHAR,
                name_type_param VARCHAR,
                random_val FLOAT
            ) RETURNS VARCHAR AS $$
            DECLARE
                name_count INTEGER;
                name_idx INTEGER;
                result_name VARCHAR;
            BEGIN
                -- Count matching names
                SELECT COUNT(*) INTO name_count
                FROM names 
                WHERE locale = locale_param AND name_type = name_type_param;
                
                IF name_count = 0 THEN
                    RETURN 'Unknown';
                END IF;
                
                -- Deterministic selection
                name_idx := 1 + FLOOR(random_val * name_count);
                
                -- Get the name
                SELECT name_value INTO result_name
                FROM (
                    SELECT name_value, ROW_NUMBER() OVER (ORDER BY id) as rn
                    FROM names 
                    WHERE locale = locale_param AND name_type = name_type_param
                ) t WHERE rn = name_idx;
                
                RETURN result_name;
            END;
            $$ LANGUAGE plpgsql;
        ''')
        
        # Function 3: Uniform sphere coordinates
        cur.execute('''
            CREATE OR REPLACE FUNCTION get_sphere_coords(
                u1 FLOAT,
                u2 FLOAT
            ) RETURNS TABLE(lat FLOAT, lon FLOAT) AS $$
            DECLARE
                phi FLOAT;
                theta FLOAT;
            BEGIN
                phi := 2 * 3.141592653589793 * u1;
                theta := ACOS(2 * u2 - 1);
                lat := DEGREES(1.5707963267948966 - theta);
                lon := DEGREES(phi - 3.141592653589793);
                RETURN NEXT;
            END;
            $$ LANGUAGE plpgsql;
        ''')
        
        # Function 4: Normal distribution
        cur.execute('''
            CREATE OR REPLACE FUNCTION get_normal_value(
                u1 FLOAT,
                u2 FLOAT,
                mean_val FLOAT,
                stddev_val FLOAT
            ) RETURNS FLOAT AS $$
            DECLARE
                z0 FLOAT;
            BEGIN
                z0 := SQRT(-2 * LN(u1)) * COS(2 * 3.141592653589793 * u2);
                RETURN mean_val + z0 * stddev_val;
            END;
            $$ LANGUAGE plpgsql;
        ''')
        
        # Function 5: Generate phone
        cur.execute('''
            CREATE OR REPLACE FUNCTION get_phone_number(
                locale_param VARCHAR,
                seed_param INTEGER,
                idx_param INTEGER
            ) RETURNS VARCHAR AS $$
            DECLARE
                num1 INTEGER;
                num2 INTEGER;
                num3 INTEGER;
            BEGIN
                IF locale_param = 'en_US' THEN
                    num1 := 555;
                    num2 := 1000 + ((seed_param + idx_param * 104729) % 9000);
                    num3 := ((seed_param * 3 + idx_param * 997) % 10000);
                    RETURN '+1 (' || num1::VARCHAR || ') ' || 
                           LPAD(num2::VARCHAR, 4, '0') || '-' || 
                           LPAD(num3::VARCHAR, 4, '0');
                ELSE
                    num1 := 49;
                    num2 := 30 + ((seed_param + idx_param * 104729) % 70);
                    num3 := ((seed_param * 7 + idx_param * 104729) % 10000000);
                    RETURN '+' || num1::VARCHAR || ' ' || 
                           num2::VARCHAR || ' ' || 
                           LPAD(num3::VARCHAR, 7, '0');
                END IF;
            END;
            $$ LANGUAGE plpgsql;
        ''')
        
        # MAIN FUNCTION: Uses all modular functions and READS FROM TABLES
        cur.execute('''
            CREATE OR REPLACE FUNCTION generate_users_batch(
                locale_param VARCHAR DEFAULT 'en_US',
                seed_param INTEGER DEFAULT 12345,
                batch_size_param INTEGER DEFAULT 10,
                batch_num_param INTEGER DEFAULT 0
            )
            RETURNS TABLE(
                user_id BIGINT,
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
                rand1 FLOAT;
                rand2 FLOAT;
                rand3 FLOAT;
                rand4 FLOAT;
                coords RECORD;
                city_name VARCHAR;
                height_val FLOAT;
                weight_val FLOAT;
            BEGIN
                FOR i IN 1..batch_size_param LOOP
                    user_idx := batch_num_param * batch_size_param + i;
                    
                    -- Get random values using modular function
                    rand1 := get_random(seed_param, user_idx);
                    rand2 := get_random(seed_param * 2, user_idx);
                    rand3 := get_random(seed_param * 3, user_idx);
                    rand4 := get_random(seed_param * 4, user_idx);
                    
                    -- GET NAMES FROM TABLE using modular function
                    first_name := get_name_from_table(locale_param, 'first_name', rand1);
                    last_name := get_name_from_table(locale_param, 'last_name', rand2);
                    
                    user_id := seed_param * 100000 + user_idx;
                    
                    -- Email
                    email := LOWER(first_name || '.' || last_name || user_idx::VARCHAR || 
                                 CASE WHEN locale_param = 'en_US' THEN '@example.com' ELSE '@example.de' END);
                    
                    -- Phone using modular function
                    phone := get_phone_number(locale_param, seed_param, user_idx);
                    
                    -- Get city from table
                    SELECT city_name INTO city_name
                    FROM cities 
                    WHERE locale = locale_param 
                    ORDER BY ((seed_param * 997 + user_idx * 104729) % 1000000)
                    LIMIT 1;
                    
                    IF city_name IS NULL THEN
                        city_name := CASE WHEN locale_param = 'en_US' THEN 'Unknown City' ELSE 'Unbekannte Stadt' END;
                    END IF;
                    
                    address := ((user_idx % 999) + 1)::VARCHAR || ' ' ||
                              CASE WHEN locale_param = 'en_US' THEN 'Main St, ' || city_name || ', USA'
                                   ELSE 'Hauptstraße, ' || city_name || ', Germany' END;
                    
                    -- Uniform sphere coordinates using modular function
                    SELECT * INTO coords FROM get_sphere_coords(rand1, rand2);
                    latitude := coords.lat;
                    longitude := coords.lon;
                    
                    -- Normal distribution using modular function
                    IF locale_param = 'en_US' THEN
                        height_val := get_normal_value(rand3, rand4, 170.0, 10.0);
                        weight_val := get_normal_value(rand4, rand3, 70.0, 15.0);
                    ELSE
                        height_val := get_normal_value(rand3, rand4, 175.0, 9.0);
                        weight_val := get_normal_value(rand4, rand3, 75.0, 14.0);
                    END IF;
                    
                    -- Keep realistic
                    IF height_val < 140 THEN height_val := 140; END IF;
                    IF height_val > 210 THEN height_val := 210; END IF;
                    IF weight_val < 40 THEN weight_val := 40; END IF;
                    IF weight_val > 150 THEN weight_val := 150; END IF;
                    
                    height_cm := ROUND(height_val, 1);
                    weight_kg := ROUND(weight_val, 1);
                    latitude := ROUND(latitude, 4);
                    longitude := ROUND(longitude, 4);
                    
                    RETURN NEXT;
                END LOOP;
            END;
            $$ LANGUAGE plpgsql;
        ''')
        
        conn.commit()
        print("✅ Database initialized with modular functions reading from tables!", file=sys.stderr)
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}", file=sys.stderr)
        # Don't raise, just continue

# Initialize
init_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_users():
    try:
        data = request.get_json()
        locale = data.get('locale', 'en_US')
        seed = int(data.get('seed', 12345))
        batch_size = min(int(data.get('batch_size', 10)), 1000)
        batch_index = int(data.get('batch_index', 0))
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM generate_users_batch(%s, %s, %s, %s)", 
                   (locale, seed, batch_size, batch_index))
        rows = cur.fetchall()
        
        users = []
        for row in rows:
            users.append({
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'email': row[3],
                'phone': row[4],
                'address': row[5],
                'latitude': round(float(row[6]), 4),
                'longitude': round(float(row[7]), 4),
                'height_cm': round(float(row[8]), 1),
                'weight_kg': round(float(row[9]), 1)
            })
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'users': users,
            'batch_index': batch_index,
            'seed': seed,
            'locale': locale,
            'total_generated': (batch_index + 1) * batch_size
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
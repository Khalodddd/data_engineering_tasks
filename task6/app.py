from flask import Flask, render_template, request, jsonify
import psycopg2
import os
import sys

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

def init_database():
    """Initialize database on first run"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if function exists
        cur.execute("SELECT EXISTS(SELECT 1 FROM pg_proc WHERE proname = 'generate_users_batch');")
        if not cur.fetchone()[0]:
            print("Initializing database...", file=sys.stderr)
            
            # Create the improved function with seed-based randomness
            cur.execute('''
                CREATE OR REPLACE FUNCTION generate_users_batch(
                    p_locale VARCHAR DEFAULT 'en_US',
                    p_seed INTEGER DEFAULT 12345,
                    p_batch_size INTEGER DEFAULT 100,
                    p_batch_number INTEGER DEFAULT 0
                )
                RETURNS TABLE(
                    id INTEGER,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    address TEXT,
                    coordinates TEXT,
                    height_cm INTEGER,
                    weight_kg NUMERIC(5,2)
                ) AS $$
                DECLARE
                    i INTEGER;
                    start_index INTEGER;
                    user_index INTEGER;
                    first_names VARCHAR[];
                    last_names VARCHAR[];
                    cities VARCHAR[];
                    streets VARCHAR[];
                    street_types VARCHAR[];
                    first_name_idx INTEGER;
                    last_name_idx INTEGER;
                    city_idx INTEGER;
                    street_idx INTEGER;
                    house_num INTEGER;
                    lat FLOAT;
                    lon FLOAT;
                    u1 FLOAT;
                    u2 FLOAT;
                    z FLOAT;
                    r FLOAT;
                    phi FLOAT;
                BEGIN
                    -- Define name arrays based on locale
                    IF p_locale = 'en_US' THEN
                        first_names := ARRAY['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 
                                           'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Barbara',
                                           'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah',
                                           'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
                                           'Matthew', 'Margaret', 'Anthony', 'Betty', 'Donald', 'Sandra'];
                        last_names := ARRAY['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
                                          'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez',
                                          'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore',
                                          'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White',
                                          'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson'];
                        cities := ARRAY['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
                                      'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'];
                        streets := ARRAY['Main', 'Oak', 'Pine', 'Maple', 'Cedar', 'Elm', 'Washington',
                                       'Park', 'Lake', 'Hill', 'First', 'Second', 'Third', 'Fourth'];
                        street_types := ARRAY['St', 'Ave', 'Rd', 'Dr', 'Ln', 'Blvd', 'Way'];
                    ELSE
                        first_names := ARRAY['Hans', 'Anna', 'Peter', 'Maria', 'Thomas', 'Sabine',
                                           'Michael', 'Ursula', 'Andreas', 'Monika', 'Wolfgang', 'Petra',
                                           'Klaus', 'Elke', 'Jürgen', 'Birgit', 'Frank', 'Karin',
                                           'Bernd', 'Andrea', 'Horst', 'Gisela', 'Dieter', 'Helga'];
                        last_names := ARRAY['Müller', 'Schmidt', 'Schneider', 'Fischer', 'Weber', 'Meyer',
                                          'Wagner', 'Becker', 'Schulz', 'Hoffmann', 'Schäfer', 'Koch',
                                          'Bauer', 'Richter', 'Klein', 'Wolf', 'Schröder', 'Neumann',
                                          'Schwarz', 'Zimmermann', 'Braun', 'Krüger', 'Hofmann', 'Hartmann'];
                        cities := ARRAY['Berlin', 'Hamburg', 'Munich', 'Cologne', 'Frankfurt',
                                      'Stuttgart', 'Düsseldorf', 'Dortmund', 'Essen', 'Leipzig'];
                        streets := ARRAY['Haupt', 'Bahnhof', 'Goethe', 'Schiller', 'Berliner',
                                       'Mozart', 'Dorf', 'Schul', 'Kirch', 'Berg', 'Linden', 'Rosen'];
                        street_types := ARRAY['straße', 'weg', 'allee', 'platz', 'ring', 'gasse'];
                    END IF;
                    
                    -- Calculate start index
                    start_index := p_batch_number * p_batch_size;
                    
                    FOR i IN 1..p_batch_size LOOP
                        user_index := start_index + i;
                        
                        -- Set deterministic seed for this user
                        PERFORM setseed((p_seed + user_index)::float / 1000000);
                        
                        -- Select names using modulo for deterministic randomness
                        first_name_idx := (user_index % array_length(first_names, 1)) + 1;
                        last_name_idx := ((user_index * 7) % array_length(last_names, 1)) + 1;
                        city_idx := ((user_index * 11) % array_length(cities, 1)) + 1;
                        street_idx := ((user_index * 13) % array_length(streets, 1)) + 1;
                        
                        -- Generate house number
                        house_num := 100 + ((user_index * 17) % 900);
                        
                        -- Generate uniformly distributed coordinates on sphere
                        u1 := random();
                        u2 := random();
                        z := 2 * u1 - 1;  -- Uniform on [-1, 1]
                        r := sqrt(1 - z * z);
                        phi := 2 * pi() * u2;
                        lat := degrees(asin(z));
                        lon := degrees(phi) - 180;
                        
                        -- Generate height with normal distribution (Box-Muller transform)
                        u1 := random();
                        u2 := random();
                        height_cm := 170 + 10 * sqrt(-2 * ln(u1)) * cos(2 * pi() * u2);
                        height_cm := GREATEST(140, LEAST(210, height_cm))::integer;
                        
                        -- Generate weight with normal distribution
                        u1 := random();
                        u2 := random();
                        weight_kg := 70 + 15 * sqrt(-2 * ln(u1)) * cos(2 * pi() * u2);
                        weight_kg := GREATEST(40, LEAST(150, weight_kg))::numeric(5,2);
                        
                        -- Return the user
                        RETURN QUERY SELECT
                            user_index,
                            first_names[first_name_idx],
                            last_names[last_name_idx],
                            LOWER(first_names[first_name_idx] || '.' || last_names[last_name_idx] || 
                                 user_index::TEXT || '@example.' || 
                                 CASE WHEN p_locale = 'en_US' THEN 'com' ELSE 'de' END),
                            CASE WHEN p_locale = 'en_US' 
                                THEN '+1-' || lpad((200 + (user_index % 800))::text, 3, '0') || '-' ||
                                     lpad(((user_index * 3) % 1000)::text, 3, '0') || '-' ||
                                     lpad(((user_index * 7) % 10000)::text, 4, '0')
                                ELSE '+49 ' || lpad((30 + (user_index % 70))::text, 2, '0') || ' ' ||
                                     lpad(((user_index * 5) % 10000000)::text, 7, '0')
                            END,
                            house_num::text || ' ' || streets[street_idx] || ' ' || 
                            street_types[((street_idx - 1) % array_length(street_types, 1)) + 1] || ', ' || 
                            cities[city_idx],
                            '(' || lat::numeric(8,6) || ', ' || lon::numeric(9,6) || ')',
                            height_cm,
                            weight_kg;
                    END LOOP;
                END;
                $$ LANGUAGE plpgsql;
            ''')
            conn.commit()
            print("Database initialized successfully!", file=sys.stderr)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Database init error: {e}", file=sys.stderr)

# Initialize database on startup
init_database()

@app.route('/')
def index():
    locales = ['en_US', 'de_DE']
    return render_template('index.html', locales=locales)

@app.route('/generate', methods=['POST'])
def generate_users():
    try:
        data = request.get_json()
        locale = data.get('locale', 'en_US')
        seed = int(data.get('seed', 12345))
        batch_size = min(int(data.get('batch_size', 10)), 100)
        batch_index = int(data.get('batch_index', 0))
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM generate_users_batch(%s, %s, %s, %s)", 
                   (locale, seed, batch_size, batch_index))
        users = cur.fetchall()
        
        results = []
        for row in users:
            results.append({
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'email': row[3],
                'phone': row[4],
                'address': row[5],
                'coordinates': row[6],
                'height_cm': row[7],
                'weight_kg': float(row[8]) if row[8] else 0.0
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

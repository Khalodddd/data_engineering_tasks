from flask import Flask, render_template, request, jsonify
import psycopg2
import os
import sys
import math

app = Flask(__name__)

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        print("Using DATABASE_URL from environment", file=sys.stderr)
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
    """Initialize database with proper function"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # FORCE DROP THE OLD FUNCTION
        cur.execute("DROP FUNCTION IF EXISTS generate_users_batch(VARCHAR, INTEGER, INTEGER, INTEGER);")
        
        print("Creating NEW generate_users_batch function...", file=sys.stderr)
        
        # Create completely NEW function with proper random seed selection
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
                first_names TEXT[];
                last_names TEXT[];
                cities TEXT[];
                streets TEXT[];
                street_types TEXT[];
                city_idx INTEGER;
                fn_idx INTEGER;
                ln_idx INTEGER;
                street_idx INTEGER;
                house_num INTEGER;
                u1 FLOAT;
                u2 FLOAT;
                z FLOAT;
                r FLOAT;
                phi FLOAT;
                lat FLOAT;
                lon FLOAT;
                height_val FLOAT;
                weight_val FLOAT;
            BEGIN
                -- Initialize arrays for USA
                IF p_locale = 'en_US' THEN
                    first_names := ARRAY['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 
                                       'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Barbara',
                                       'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah',
                                       'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
                                       'Matthew', 'Margaret', 'Anthony', 'Betty', 'Donald', 'Sandra',
                                       'Mark', 'Ashley', 'Paul', 'Dorothy', 'Steven', 'Kimberly',
                                       'Andrew', 'Emily', 'Kenneth', 'Donna', 'Joshua', 'Michelle',
                                       'Kevin', 'Carol', 'Brian', 'Amanda', 'George', 'Melissa',
                                       'Edward', 'Deborah', 'Ronald', 'Stephanie', 'Timothy', 'Rebecca'];
                    
                    last_names := ARRAY['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
                                      'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez',
                                      'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore',
                                      'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White',
                                      'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
                                      'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott',
                                      'Torres', 'Nguyen', 'Hill', 'Flores', 'Green', 'Adams',
                                      'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell'];
                    
                    cities := ARRAY['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
                                  'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
                                  'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'Charlotte',
                                  'Indianapolis', 'San Francisco', 'Seattle', 'Denver', 'Washington'];
                    
                    streets := ARRAY['Main', 'Oak', 'Pine', 'Maple', 'Cedar', 'Elm', 'Washington',
                                   'Park', 'Lake', 'Hill', 'First', 'Second', 'Third', 'Fourth',
                                   'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth'];
                    
                    street_types := ARRAY['St', 'Ave', 'Rd', 'Dr', 'Ln', 'Blvd', 'Way', 'Court'];
                
                -- Initialize arrays for Germany
                ELSE
                    first_names := ARRAY['Hans', 'Anna', 'Peter', 'Maria', 'Thomas', 'Sabine',
                                       'Michael', 'Ursula', 'Andreas', 'Monika', 'Wolfgang', 'Petra',
                                       'Klaus', 'Elke', 'Jürgen', 'Birgit', 'Frank', 'Karin',
                                       'Bernd', 'Andrea', 'Horst', 'Gisela', 'Dieter', 'Helga',
                                       'Walter', 'Ingrid', 'Stefan', 'Renate', 'Manfred', 'Christine',
                                       'Heinz', 'Brigitte', 'Rolf', 'Angelika', 'Karl', 'Susanne',
                                       'Gerhard', 'Gabriele', 'Christian', 'Martina', 'Uwe', 'Daniela',
                                       'Helmut', 'Cornelia', 'Rainer', 'Silke', 'Joachim', 'Kerstin'];
                    
                    last_names := ARRAY['Müller', 'Schmidt', 'Schneider', 'Fischer', 'Weber', 'Meyer',
                                      'Wagner', 'Becker', 'Schulz', 'Hoffmann', 'Schäfer', 'Koch',
                                      'Bauer', 'Richter', 'Klein', 'Wolf', 'Schröder', 'Neumann',
                                      'Schwarz', 'Zimmermann', 'Braun', 'Krüger', 'Hofmann', 'Hartmann',
                                      'Lange', 'Schmitt', 'Werner', 'Schmitz', 'Krause', 'Meier',
                                      'Lehmann', 'Schmid', 'Schulze', 'Maier', 'Köhler', 'Herrmann',
                                      'Walter', 'König', 'Mayer', 'Huber', 'Kaiser', 'Fuchs',
                                      'Peters', 'Lang', 'Scholz', 'Möller', 'Weiß', 'Jung'];
                    
                    cities := ARRAY['Berlin', 'Hamburg', 'Munich', 'Cologne', 'Frankfurt',
                                  'Stuttgart', 'Düsseldorf', 'Dortmund', 'Essen', 'Leipzig',
                                  'Bremen', 'Dresden', 'Hanover', 'Nuremberg', 'Duisburg',
                                  'Bochum', 'Wuppertal', 'Bielefeld', 'Bonn', 'Münster'];
                    
                    streets := ARRAY['Haupt', 'Bahnhof', 'Goethe', 'Schiller', 'Berliner',
                                   'Mozart', 'Dorf', 'Schul', 'Kirch', 'Berg', 'Linden',
                                   'Rosen', 'Birken', 'Eichen', 'Buchen', 'Ahorn', 'Kastanien',
                                   'Tannen', 'Fichten', 'Kiefern'];
                    
                    street_types := ARRAY['straße', 'weg', 'allee', 'platz', 'ring', 'gasse'];
                END IF;
                
                -- Generate users
                FOR i IN 1..p_batch_size LOOP
                    user_idx := p_batch_number * p_batch_size + i;
                    
                    -- Set seed for deterministic randomness
                    PERFORM setseed((p_seed + user_idx * 997)::float / 1000000.0);
                    
                    -- Use modulo with large prime multiplication for better distribution
                    fn_idx := ((user_idx * 104729) % array_length(first_names, 1)) + 1;
                    ln_idx := ((user_idx * 224737) % array_length(last_names, 1)) + 1;
                    city_idx := ((user_idx * 367957) % array_length(cities, 1)) + 1;
                    street_idx := ((user_idx * 448939) % array_length(streets, 1)) + 1;
                    
                    -- Generate house number (1-9999)
                    house_num := ((user_idx * 59999) % 9999) + 1;
                    
                    -- Generate UNIFORMLY distributed coordinates on sphere
                    u1 := random();
                    u2 := random();
                    z := 2.0 * u1 - 1.0;  -- Uniform on [-1, 1]
                    r := sqrt(1.0 - z * z);
                    phi := 2.0 * pi() * u2;
                    
                    -- Convert to latitude/longitude
                    lat := asin(z) * 180.0 / pi();  -- Latitude in [-90, 90]
                    lon := (phi * 180.0 / pi()) - 180.0;  -- Longitude in [-180, 180]
                    
                    -- Generate height with NORMAL distribution (Box-Muller transform)
                    u1 := random();
                    u2 := random();
                    height_val := sqrt(-2.0 * ln(u1)) * cos(2.0 * pi() * u2);
                    height_val := 170.0 + height_val * 10.0;  -- Mean 170cm, SD 10cm
                    
                    -- Ensure realistic height range
                    IF height_val < 140.0 THEN
                        height_val := 140.0;
                    ELSIF height_val > 210.0 THEN
                        height_val := 210.0;
                    END IF;
                    
                    -- Generate weight with NORMAL distribution
                    u1 := random();
                    u2 := random();
                    weight_val := sqrt(-2.0 * ln(u1)) * cos(2.0 * pi() * u2);
                    weight_val := 70.0 + weight_val * 15.0;  -- Mean 70kg, SD 15kg
                    
                    -- Ensure realistic weight range
                    IF weight_val < 40.0 THEN
                        weight_val := 40.0;
                    ELSIF weight_val > 150.0 THEN
                        weight_val := 150.0;
                    END IF;
                    
                    -- Return the user
                    id := p_seed * 100000 + user_idx;
                    first_name := first_names[fn_idx];
                    last_name := last_names[ln_idx];
                    email := LOWER(first_name || '.' || last_name || user_idx::TEXT || 
                                 CASE WHEN p_locale = 'en_US' THEN '@example.com' ELSE '@example.de' END);
                    
                    -- Generate phone number
                    IF p_locale = 'en_US' THEN
                        phone := '+1-' || 
                                lpad((((user_idx * 3) % 899) + 100)::text, 3, '0') || '-' ||
                                lpad((((user_idx * 7) % 899) + 100)::text, 3, '0') || '-' ||
                                lpad((((user_idx * 11) % 8999) + 1000)::text, 4, '0');
                    ELSE
                        phone := '+49 ' || 
                                lpad((((user_idx * 5) % 89) + 10)::text, 2, '0') || ' ' ||
                                lpad((((user_idx * 13) % 9999999) + 1000000)::text, 7, '0');
                    END IF;
                    
                    address := house_num::text || ' ' || 
                             streets[street_idx] || ' ' || 
                             street_types[((street_idx - 1) % array_length(street_types, 1)) + 1] || ', ' || 
                             cities[city_idx];
                    
                    latitude := lat;
                    longitude := lon;
                    height_cm := ROUND(height_val, 1);
                    weight_kg := ROUND(weight_val, 1);
                    
                    RETURN NEXT;
                END LOOP;
            END;
            $$ LANGUAGE plpgsql;
        ''')
        
        conn.commit()
        print("✅ NEW function created successfully!", file=sys.stderr)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database init error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

# Initialize on import
print("🚀 Starting app, initializing database...", file=sys.stderr)
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
                'latitude': float(row[6]) if row[6] else 0.0,
                'longitude': float(row[7]) if row[7] else 0.0,
                'height_cm': float(row[8]) if row[8] else 0.0,
                'weight_kg': float(row[9]) if row[9] else 0.0
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
        print(f"Error in generate_users: {e}", file=sys.stderr)
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, render_template, request, jsonify
import psycopg2
import os
import sys
import time
from datetime import datetime
import math

app = Flask(__name__)

def get_db_connection():
    """Connect to PostgreSQL with SSL fix for Render"""
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        print(f"Connecting to: {database_url[:50]}...", file=sys.stderr)
        
        # Fix postgres:// to postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://')
        
        try:
            # Try with SSL first
            return psycopg2.connect(database_url, sslmode='require')
        except Exception as e:
            print(f"SSL connection failed: {e}", file=sys.stderr)
            print("Trying without SSL...", file=sys.stderr)
            # Fallback without SSL
            try:
                return psycopg2.connect(database_url, sslmode='disable')
            except Exception as e2:
                print(f"Connection failed: {e2}", file=sys.stderr)
                raise
    else:
        # Local development
        print("Using local PostgreSQL...", file=sys.stderr)
        return psycopg2.connect(
            dbname=os.environ.get('DB_NAME', 'fake_user_data'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', ''),
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432')
        )

def init_database():
    """Initialize database with tables and function"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("Creating required tables...", file=sys.stderr)
        
        # 1. CREATE NAMES TABLE (REQUIRED by assignment)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS names (
                id SERIAL PRIMARY KEY,
                locale VARCHAR(10) NOT NULL,
                name_type VARCHAR(20) NOT NULL,
                name_value VARCHAR(100) NOT NULL,
                gender VARCHAR(10),
                frequency INTEGER DEFAULT 1
            );
        ''')
        
        # 2. Insert sample names data (minimum required)
        print("Inserting names data...", file=sys.stderr)
        
        # Clear any existing data
        cur.execute("DELETE FROM names;")
        
        # USA first names (50 male, 50 female)
        usa_names = [
            # Male first names
            ('en_US', 'first_name', 'James', 'male'), ('en_US', 'first_name', 'John', 'male'),
            ('en_US', 'first_name', 'Robert', 'male'), ('en_US', 'first_name', 'Michael', 'male'),
            ('en_US', 'first_name', 'William', 'male'), ('en_US', 'first_name', 'David', 'male'),
            ('en_US', 'first_name', 'Richard', 'male'), ('en_US', 'first_name', 'Joseph', 'male'),
            ('en_US', 'first_name', 'Thomas', 'male'), ('en_US', 'first_name', 'Charles', 'male'),
            ('en_US', 'first_name', 'Christopher', 'male'), ('en_US', 'first_name', 'Daniel', 'male'),
            ('en_US', 'first_name', 'Matthew', 'male'), ('en_US', 'first_name', 'Anthony', 'male'),
            ('en_US', 'first_name', 'Donald', 'male'), ('en_US', 'first_name', 'Mark', 'male'),
            ('en_US', 'first_name', 'Paul', 'male'), ('en_US', 'first_name', 'Steven', 'male'),
            ('en_US', 'first_name', 'Andrew', 'male'), ('en_US', 'first_name', 'Kenneth', 'male'),
            ('en_US', 'first_name', 'Joshua', 'male'), ('en_US', 'first_name', 'Kevin', 'male'),
            ('en_US', 'first_name', 'Brian', 'male'), ('en_US', 'first_name', 'George', 'male'),
            ('en_US', 'first_name', 'Edward', 'male'), ('en_US', 'first_name', 'Ronald', 'male'),
            ('en_US', 'first_name', 'Timothy', 'male'), ('en_US', 'first_name', 'Jason', 'male'),
            ('en_US', 'first_name', 'Jeffrey', 'male'), ('en_US', 'first_name', 'Ryan', 'male'),
            ('en_US', 'first_name', 'Jacob', 'male'), ('en_US', 'first_name', 'Gary', 'male'),
            ('en_US', 'first_name', 'Nicholas', 'male'), ('en_US', 'first_name', 'Eric', 'male'),
            ('en_US', 'first_name', 'Stephen', 'male'), ('en_US', 'first_name', 'Jonathan', 'male'),
            ('en_US', 'first_name', 'Larry', 'male'), ('en_US', 'first_name', 'Justin', 'male'),
            ('en_US', 'first_name', 'Scott', 'male'), ('en_US', 'first_name', 'Brandon', 'male'),
            ('en_US', 'first_name', 'Benjamin', 'male'), ('en_US', 'first_name', 'Samuel', 'male'),
            ('en_US', 'first_name', 'Gregory', 'male'), ('en_US', 'first_name', 'Frank', 'male'),
            ('en_US', 'first_name', 'Alexander', 'male'), ('en_US', 'first_name', 'Raymond', 'male'),
            ('en_US', 'first_name', 'Patrick', 'male'), ('en_US', 'first_name', 'Jack', 'male'),
            ('en_US', 'first_name', 'Dennis', 'male'), ('en_US', 'first_name', 'Jerry', 'male'),
            
            # Female first names
            ('en_US', 'first_name', 'Mary', 'female'), ('en_US', 'first_name', 'Patricia', 'female'),
            ('en_US', 'first_name', 'Jennifer', 'female'), ('en_US', 'first_name', 'Linda', 'female'),
            ('en_US', 'first_name', 'Elizabeth', 'female'), ('en_US', 'first_name', 'Barbara', 'female'),
            ('en_US', 'first_name', 'Susan', 'female'), ('en_US', 'first_name', 'Jessica', 'female'),
            ('en_US', 'first_name', 'Sarah', 'female'), ('en_US', 'first_name', 'Karen', 'female'),
            ('en_US', 'first_name', 'Nancy', 'female'), ('en_US', 'first_name', 'Lisa', 'female'),
            ('en_US', 'first_name', 'Margaret', 'female'), ('en_US', 'first_name', 'Sandra', 'female'),
            ('en_US', 'first_name', 'Ashley', 'female'), ('en_US', 'first_name', 'Kimberly', 'female'),
            ('en_US', 'first_name', 'Emily', 'female'), ('en_US', 'first_name', 'Donna', 'female'),
            ('en_US', 'first_name', 'Michelle', 'female'), ('en_US', 'first_name', 'Dorothy', 'female'),
            ('en_US', 'first_name', 'Carol', 'female'), ('en_US', 'first_name', 'Amanda', 'female'),
            ('en_US', 'first_name', 'Melissa', 'female'), ('en_US', 'first_name', 'Deborah', 'female'),
            ('en_US', 'first_name', 'Stephanie', 'female'), ('en_US', 'first_name', 'Rebecca', 'female'),
            ('en_US', 'first_name', 'Laura', 'female'), ('en_US', 'first_name', 'Sharon', 'female'),
            ('en_US', 'first_name', 'Cynthia', 'female'), ('en_US', 'first_name', 'Kathleen', 'female'),
            ('en_US', 'first_name', 'Amy', 'female'), ('en_US', 'first_name', 'Shirley', 'female'),
            ('en_US', 'first_name', 'Angela', 'female'), ('en_US', 'first_name', 'Helen', 'female'),
            ('en_US', 'first_name', 'Anna', 'female'), ('en_US', 'first_name', 'Brenda', 'female'),
            ('en_US', 'first_name', 'Pamela', 'female'), ('en_US', 'first_name', 'Nicole', 'female'),
            ('en_US', 'first_name', 'Samantha', 'female'), ('en_US', 'first_name', 'Katherine', 'female'),
            ('en_US', 'first_name', 'Emma', 'female'), ('en_US', 'first_name', 'Ruth', 'female'),
            ('en_US', 'first_name', 'Christine', 'female'), ('en_US', 'first_name', 'Catherine', 'female'),
            ('en_US', 'first_name', 'Debra', 'female'), ('en_US', 'first_name', 'Rachel', 'female'),
            ('en_US', 'first_name', 'Carolyn', 'female'), ('en_US', 'first_name', 'Janet', 'female'),
            ('en_US', 'first_name', 'Virginia', 'female'), ('en_US', 'first_name', 'Maria', 'female'),
        ]
        
        # German first names
        german_names = [
            # Male first names
            ('de_DE', 'first_name', 'Hans', 'male'), ('de_DE', 'first_name', 'Peter', 'male'),
            ('de_DE', 'first_name', 'Thomas', 'male'), ('de_DE', 'first_name', 'Michael', 'male'),
            ('de_DE', 'first_name', 'Andreas', 'male'), ('de_DE', 'first_name', 'Wolfgang', 'male'),
            ('de_DE', 'first_name', 'Klaus', 'male'), ('de_DE', 'first_name', 'Werner', 'male'),
            ('de_DE', 'first_name', 'Frank', 'male'), ('de_DE', 'first_name', 'Stefan', 'male'),
            ('de_DE', 'first_name', 'Martin', 'male'), ('de_DE', 'first_name', 'Ulrich', 'male'),
            ('de_DE', 'first_name', 'Jürgen', 'male'), ('de_DE', 'first_name', 'Heinz', 'male'),
            ('de_DE', 'first_name', 'Karl', 'male'), ('de_DE', 'first_name', 'Walter', 'male'),
            ('de_DE', 'first_name', 'Bernd', 'male'), ('de_DE', 'first_name', 'Horst', 'male'),
            ('de_DE', 'first_name', 'Dieter', 'male'), ('de_DE', 'first_name', 'Manfred', 'male'),
            ('de_DE', 'first_name', 'Gerhard', 'male'), ('de_DE', 'first_name', 'Günter', 'male'),
            ('de_DE', 'first_name', 'Helmut', 'male'), ('de_DE', 'first_name', 'Rolf', 'male'),
            ('de_DE', 'first_name', 'Friedrich', 'male'), ('de_DE', 'first_name', 'Rainer', 'male'),
            
            # Female first names
            ('de_DE', 'first_name', 'Anna', 'female'), ('de_DE', 'first_name', 'Maria', 'female'),
            ('de_DE', 'first_name', 'Sabine', 'female'), ('de_DE', 'first_name', 'Ursula', 'female'),
            ('de_DE', 'first_name', 'Monika', 'female'), ('de_DE', 'first_name', 'Petra', 'female'),
            ('de_DE', 'first_name', 'Elisabeth', 'female'), ('de_DE', 'first_name', 'Christine', 'female'),
            ('de_DE', 'first_name', 'Karin', 'female'), ('de_DE', 'first_name', 'Helga', 'female'),
            ('de_DE', 'first_name', 'Brigitte', 'female'), ('de_DE', 'first_name', 'Ingrid', 'female'),
            ('de_DE', 'first_name', 'Erika', 'female'), ('de_DE', 'first_name', 'Gisela', 'female'),
            ('de_DE', 'first_name', 'Claudia', 'female'), ('de_DE', 'first_name', 'Susanne', 'female'),
            ('de_DE', 'first_name', 'Renate', 'female'), ('de_DE', 'first_name', 'Andrea', 'female'),
            ('de_DE', 'first_name', 'Silke', 'female'), ('de_DE', 'first_name', 'Martina', 'female'),
            ('de_DE', 'first_name', 'Daniela', 'female'), ('de_DE', 'first_name', 'Stefanie', 'female'),
            ('de_DE', 'first_name', 'Heike', 'female'), ('de_DE', 'first_name', 'Birgit', 'female'),
            ('de_DE', 'first_name', 'Julia', 'female'), ('de_DE', 'first_name', 'Katharina', 'female'),
        ]
        
        # Last names for both locales
        last_names = [
            # USA last names
            ('en_US', 'last_name', 'Smith'), ('en_US', 'last_name', 'Johnson'),
            ('en_US', 'last_name', 'Williams'), ('en_US', 'last_name', 'Brown'),
            ('en_US', 'last_name', 'Jones'), ('en_US', 'last_name', 'Garcia'),
            ('en_US', 'last_name', 'Miller'), ('en_US', 'last_name', 'Davis'),
            ('en_US', 'last_name', 'Rodriguez'), ('en_US', 'last_name', 'Martinez'),
            ('en_US', 'last_name', 'Hernandez'), ('en_US', 'last_name', 'Lopez'),
            ('en_US', 'last_name', 'Gonzalez'), ('en_US', 'last_name', 'Wilson'),
            ('en_US', 'last_name', 'Anderson'), ('en_US', 'last_name', 'Thomas'),
            ('en_US', 'last_name', 'Taylor'), ('en_US', 'last_name', 'Moore'),
            ('en_US', 'last_name', 'Jackson'), ('en_US', 'last_name', 'Martin'),
            ('en_US', 'last_name', 'Lee'), ('en_US', 'last_name', 'Perez'),
            ('en_US', 'last_name', 'Thompson'), ('en_US', 'last_name', 'White'),
            ('en_US', 'last_name', 'Harris'), ('en_US', 'last_name', 'Sanchez'),
            
            # German last names
            ('de_DE', 'last_name', 'Müller'), ('de_DE', 'last_name', 'Schmidt'),
            ('de_DE', 'last_name', 'Schneider'), ('de_DE', 'last_name', 'Fischer'),
            ('de_DE', 'last_name', 'Weber'), ('de_DE', 'last_name', 'Meyer'),
            ('de_DE', 'last_name', 'Wagner'), ('de_DE', 'last_name', 'Becker'),
            ('de_DE', 'last_name', 'Hoffmann'), ('de_DE', 'last_name', 'Schulz'),
            ('de_DE', 'last_name', 'Koch'), ('de_DE', 'last_name', 'Bauer'),
            ('de_DE', 'last_name', 'Richter'), ('de_DE', 'last_name', 'Klein'),
            ('de_DE', 'last_name', 'Wolf'), ('de_DE', 'last_name', 'Schröder'),
            ('de_DE', 'last_name', 'Neumann'), ('de_DE', 'last_name', 'Schwarz'),
            ('de_DE', 'last_name', 'Zimmermann'), ('de_DE', 'last_name', 'Braun'),
            ('de_DE', 'last_name', 'Hofmann'), ('de_DE', 'last_name', 'Schmitz'),
            ('de_DE', 'last_name', 'Hartmann'), ('de_DE', 'last_name', 'Krüger'),
            ('de_DE', 'last_name', 'Lange'), ('de_DE', 'last_name', 'Werner'),
        ]
        
        # Insert all names
        all_names = usa_names + german_names + last_names
        for name in all_names:
            cur.execute(
                "INSERT INTO names (locale, name_type, name_value, gender) VALUES (%s, %s, %s, %s)",
                name
            )
        
        print(f"Inserted {len(all_names)} names into database", file=sys.stderr)
        
        # 3. CREATE THE GENERATION FUNCTION (UPDATED VERSION)
        print("Creating/updating database function...", file=sys.stderr)
        
        cur.execute('''
            CREATE OR REPLACE FUNCTION generate_users_batch(
                p_locale VARCHAR DEFAULT 'en_US',
                p_seed INTEGER DEFAULT 12345,
                p_batch_size INTEGER DEFAULT 10,
                p_batch_number INTEGER DEFAULT 0
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
                base_seed BIGINT;
                rand1 FLOAT;
                rand2 FLOAT;
                
                -- Variables for normal distribution
                u1 FLOAT;
                u2 FLOAT;
                z0 FLOAT;
                z1 FLOAT;
                radius FLOAT;
                
                -- Variables for uniform sphere
                phi FLOAT;
                theta FLOAT;
                
                -- Name variables
                selected_first_name VARCHAR;
                selected_last_name VARCHAR;
                first_name_count INTEGER;
                last_name_count INTEGER;
                
            BEGIN
                FOR i IN 1..p_batch_size LOOP
                    user_idx := p_batch_number * p_batch_size + i;
                    base_seed := p_seed * 997 + user_idx * 104729;
                    
                    -- Deterministic random values
                    rand1 := (base_seed % 10000) / 10000.0;
                    rand2 := ((base_seed * 3) % 10000) / 10000.0;
                    
                    -- SELECT RANDOM FIRST NAME FROM NAMES TABLE
                    SELECT name_value INTO selected_first_name
                    FROM names 
                    WHERE locale = p_locale 
                    AND name_type = 'first_name'
                    AND (gender = 'male' OR gender = 'female')
                    ORDER BY MOD(base_seed + id, 1000000)
                    LIMIT 1;
                    
                    -- SELECT RANDOM LAST NAME FROM NAMES TABLE
                    SELECT name_value INTO selected_last_name
                    FROM names 
                    WHERE locale = p_locale 
                    AND name_type = 'last_name'
                    ORDER BY MOD(base_seed * 2 + id, 1000000)
                    LIMIT 1;
                    
                    -- If no names found, use defaults
                    IF selected_first_name IS NULL THEN
                        selected_first_name := CASE WHEN p_locale = 'en_US' THEN 'John' ELSE 'Hans' END;
                    END IF;
                    
                    IF selected_last_name IS NULL THEN
                        selected_last_name := CASE WHEN p_locale = 'en_US' THEN 'Doe' ELSE 'Müller' END;
                    END IF;
                    
                    -- Generate user
                    user_id := p_seed * 100000 + user_idx;
                    first_name := selected_first_name;
                    last_name := selected_last_name;
                    
                    -- Email
                    email := LOWER(
                        REPLACE(first_name, ' ', '') || '.' || 
                        REPLACE(last_name, ' ', '') || user_idx::TEXT || 
                        CASE WHEN p_locale = 'en_US' THEN '@example.com' ELSE '@example.de' END
                    );
                    
                    -- Phone (locale-specific formats)
                    IF p_locale = 'en_US' THEN
                        phone := '+1 (' || LPAD((555 + MOD(user_idx, 445))::TEXT, 3, '0') || ') ' || 
                                 LPAD((MOD(user_idx, 9000) + 1000)::TEXT, 3, '0') || '-' || 
                                 LPAD((MOD(user_idx * 7, 10000))::TEXT, 4, '0');
                    ELSE
                        phone := '+49 ' || LPAD((MOD(user_idx, 90) + 10)::TEXT, 2, '0') || ' ' || 
                                 LPAD((MOD(user_idx * 1000, 10000000))::TEXT, 7, '0');
                    END IF;
                    
                    -- Address (simple deterministic address)
                    address := (MOD(user_idx, 999) + 1)::TEXT || ' ' ||
                              CASE WHEN p_locale = 'en_US' THEN 
                                  CASE MOD(user_idx, 4)
                                      WHEN 0 THEN 'Main St'
                                      WHEN 1 THEN 'Oak Ave'
                                      WHEN 2 THEN 'Pine Rd'
                                      ELSE 'Maple Blvd'
                                  END || ', ' ||
                                  CASE MOD(user_idx, 5)
                                      WHEN 0 THEN 'New York'
                                      WHEN 1 THEN 'Los Angeles'
                                      WHEN 2 THEN 'Chicago'
                                      WHEN 3 THEN 'Houston'
                                      ELSE 'Phoenix'
                                  END || ', USA'
                              ELSE
                                  CASE MOD(user_idx, 4)
                                      WHEN 0 THEN 'Hauptstraße'
                                      WHEN 1 THEN 'Bahnhofweg'
                                      WHEN 2 THEN 'Goetheallee'
                                      ELSE 'Schillerstraße'
                                  END || ', ' ||
                                  CASE MOD(user_idx, 5)
                                      WHEN 0 THEN 'Berlin'
                                      WHEN 1 THEN 'Hamburg'
                                      WHEN 2 THEN 'Munich'
                                      WHEN 3 THEN 'Cologne'
                                      ELSE 'Frankfurt'
                                  END || ', Germany'
                              END;
                    
                    -- UNIFORM SPHERE COORDINATES (Marsaglia's method)
                    u1 := rand1;
                    u2 := rand2;
                    
                    -- Generate random point on sphere
                    phi := 2 * pi() * u1;
                    theta := ACOS(2 * u2 - 1);
                    
                    -- Convert to latitude/longitude
                    latitude := DEGREES(pi()/2 - theta);
                    longitude := DEGREES(phi - pi());
                    
                    -- NORMAL DISTRIBUTION for height/weight (Box-Muller transform)
                    u1 := (MOD(base_seed, 10000) + 1) / 10001.0;
                    u2 := (MOD(base_seed * 3, 10000) + 1) / 10001.0;
                    
                    z0 := SQRT(-2 * LN(u1)) * COS(2 * pi() * u2);
                    z1 := SQRT(-2 * LN(u1)) * SIN(2 * pi() * u2);
                    
                    -- Height: normal distribution ~N(170, 10) for en_US, ~N(175, 9) for de_DE
                    IF p_locale = 'en_US' THEN
                        height_cm := 170.0 + z0 * 10.0;
                    ELSE
                        height_cm := 175.0 + z0 * 9.0;
                    END IF;
                    
                    -- Weight: normal distribution ~N(70, 15) for en_US, ~N(75, 14) for de_DE
                    IF p_locale = 'en_US' THEN
                        weight_kg := 70.0 + z1 * 15.0;
                    ELSE
                        weight_kg := 75.0 + z1 * 14.0;
                    END IF;
                    
                    -- Ensure realistic ranges
                    IF height_cm < 140 THEN height_cm := 140; END IF;
                    IF height_cm > 210 THEN height_cm := 210; END IF;
                    IF weight_kg < 40 THEN weight_kg := 40; END IF;
                    IF weight_kg > 150 THEN weight_kg := 150; END IF;
                    
                    -- Round to 1 decimal
                    height_cm := ROUND(height_cm::NUMERIC, 1);
                    weight_kg := ROUND(weight_kg::NUMERIC, 1);
                    latitude := ROUND(latitude::NUMERIC, 4);
                    longitude := ROUND(longitude::NUMERIC, 4);
                    
                    RETURN NEXT;
                END LOOP;
            END;
            $$ LANGUAGE plpgsql;
        ''')
        
        conn.commit()
        print("✅ Database initialized with tables and function!", file=sys.stderr)
        
        # Verify setup
        cur.execute("SELECT COUNT(*) FROM names;")
        name_count = cur.fetchone()[0]
        print(f"✅ Total names in database: {name_count}", file=sys.stderr)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}", file=sys.stderr)
        raise

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
        
        # CALL FUNCTION
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
    <p>Proper implementation with database tables, uniform sphere coordinates, and normal distribution.</p>
    <p><strong>Features:</strong></p>
    <ul>
        <li>✅ Single names table with locale field</li>
        <li>✅ 100+ names for each locale</li>
        <li>✅ Uniform sphere coordinates</li>
        <li>✅ Normal distribution for height/weight</li>
        <li>✅ Seed-based reproducibility</li>
        <li>✅ Batch generation</li>
    </ul>
    <p><strong>Author:</strong> Khaled Soliman</p>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
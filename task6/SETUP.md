# Setup for Task 6

## 1. Install dependencies
pip install -r requirements.txt

## 2. Setup PostgreSQL database
sudo -u postgres psql -c "CREATE DATABASE fake_user_data;"
sudo -u postgres psql -d fake_user_data -c "
CREATE TABLE names (id SERIAL, locale VARCHAR(10), name_type VARCHAR(20), name_value VARCHAR(100));
CREATE TABLE generated_users (id SERIAL, locale VARCHAR(10), seed BIGINT, batch_index INT, user_index INT, full_name VARCHAR(200), address TEXT, latitude FLOAT, longitude FLOAT, height_cm FLOAT, weight_kg FLOAT, phone VARCHAR(50), email VARCHAR(200), created_at TIMESTAMP DEFAULT NOW());
"

## 3. Run the application
python app.py

## 4. Open browser
http://localhost:5000

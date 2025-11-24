import json
import re
import mysql.connector
from getpass import getpass

# File path
INPUT_FILE = "task1_d.json"

# 1️⃣ Connect to MySQL
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password=getpass("Enter MySQL password: "),
    database="task1_db",
    auth_plugin='mysql_native_password'
)
cur = conn.cursor()
print("🎉 Connected to MySQL")

# 2️⃣ Read raw file
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw = f.read()

# 3️⃣ Extract & clean JSON objects (YOUR EXACT METHOD)
records = re.findall(r'\{.*?\}', raw, re.DOTALL)
data = []
#key => value or key: value     
for obj in records:
    obj = re.sub(r':(\w+)\s*=>', r'"\1":', obj)   # :key=> → "key":
    obj = re.sub(r':(\w+)\s*:', r'"\1":', obj)    # :key: → "key":
    try:
        data.append(json.loads(obj))
    except:
        pass

print(f"✔ Parsed: {len(data)} records")

# 4️⃣ Create MySQL table
cur.execute("DROP TABLE IF EXISTS books_raw;")
cur.execute("""
CREATE TABLE books_raw (
    id TEXT,
    title TEXT,
    author TEXT,
    genre TEXT,
    publisher TEXT,
    year INT,
    price TEXT
);
""")

# 5️⃣ Insert data into MySQL
for item in data:
    cur.execute(
        "INSERT INTO books_raw VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (
            str(item["id"]),
            item.get("title"),
            item.get("author"),
            item.get("genre"),
            item.get("publisher"),
            item.get("year"),
            item.get("price")
        )
    )
conn.commit()
print("💾 Inserted into books_raw")

# 6️⃣ SQL transformation (INSIDE MySQL, same logic adapted)
cur.execute("DROP TABLE IF EXISTS book_summary;")
cur.execute("""
CREATE TABLE book_summary AS
SELECT 
    year AS publication_year,
    COUNT(*) AS book_count,
    ROUND(AVG(
        CASE
            WHEN price LIKE '€%' THEN CAST(SUBSTRING(price, 2) AS DECIMAL(10,2)) * 1.2
            WHEN price LIKE '$%' THEN CAST(SUBSTRING(price, 2) AS DECIMAL(10,2))
            ELSE NULL
        END
    ), 2) AS average_price
FROM books_raw
GROUP BY year
ORDER BY year;
""")
conn.commit()

# 7️⃣ Output summary
cur.execute("SELECT COUNT(*) FROM book_summary;")
print("📊 Summary rows:", cur.fetchone()[0])

cur.execute("SELECT * FROM book_summary LIMIT 5;")
print("🔍 Sample results:")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
print("🎯 Done")

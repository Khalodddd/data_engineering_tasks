# 📘 Itransition Internship – Data & Engineering Tasks

### Author: **Khaled Soliman**

This repository contains all internship assignment solutions for **Itransition – Data**.  
Each task includes its own folder with implementation, dataset, code, and video demonstration.

---

## 📁 Tasks Overview

| Task | Description | Status |
|------|-------------|--------|
| Task 1 | Data ingestion, regex parsing, SQL transformation | ✔ Completed |

---

## 🔧 Technologies Used
- Python (regex, mysql.connector)
- MySQL (Workbench, SQLTools in VS Code)
- VS Code
- Git & GitHub
- Data transformation using pure SQL
- JSON processing & cleansing

---

## 📊 SQL Transformation Example

```sql
CREATE TABLE book_summary AS
SELECT 
    year AS publication_year,
    COUNT(*) AS book_count,
    ROUND(AVG(
        CASE
            WHEN price LIKE '€%' THEN CAST(SUBSTR(price, 2) AS DECIMAL(10,2)) * 1.2
            WHEN price LIKE '$%' THEN CAST(SUBSTR(price, 2) AS DECIMAL(10,2))
        END
    ), 2) AS average_price
FROM books_raw
GROUP BY year
ORDER BY year;
```

---

## 📹 Video Demonstration
**Task 1:** https://drive.google.com/file/d/1e_e8rBTWokLCQlGkkj8G6p2hGgXzAdug/view

---

## 📬 Contact
- **Email:** khaled.soliman@example.com

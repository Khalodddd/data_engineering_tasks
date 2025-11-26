# Task 3 – Web Method (LCM Calculator)

This project implements an HTTP GET web method using **Python (Flask)** that accepts two natural numbers `x` and `y`, and returns their **lowest common multiple** (LCM).

The result is returned as a **plain string containing only digits**, with **no extra spaces, tags, or formatting**.  
If either `x` or `y` is not a non-negative integer, the method returns:

```
NaN
```

---

## 📁 Project Structure

```
task3/
│── app.py
│── requirements.txt
│── README.md
```

---

## ⚙️ Setup Instructions

```bash
# (Optional) Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# OR
source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

The server will start on:
```
http://127.0.0.1:5000
```

---

## 🔗 API Usage

The endpoint uses your email with **`@` and `.` replaced by `_`**:

```
/khaledsoliman1599_gmail_com?x=<value>&y=<value>
```

### Examples

| Request URL | Output |
|-------------|--------|
| `http://127.0.0.1:5000/khaledsoliman1599_gmail_com?x=12&y=18` | `36` |
| `http://127.0.0.1:5000/khaledsoliman1599_gmail_com?x=3002399751580331&y=3` | `9007199254740993` |
| `http://127.0.0.1:5000/khaledsoliman1599_gmail_com?x=-1&y=10` | `NaN` |

---

## 💻 Source Code (excerpt)

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/khaledsoliman1599_gmail_com')
def lcm():
    try:
        x = int(request.args.get("x"))
        y = int(request.args.get("y"))
        if x < 0 or y < 0:
            return "NaN"
        # LCM calculation
        import math
        return str(abs(x * y) // math.gcd(x, y))
    except:
        return "NaN"

if __name__ == "__main__":
    app.run()
```

---

## 📦 Dependencies

```
Flask==3.0.3
```

---

## 🚀 Deployment Details

The API was successfully deployed using **PythonAnywhere**.

| Configuration | Value |
|---------------|--------|
| Hosting Platform | PythonAnywhere |
| Python Version (Local) | 3.13.3 |
| PythonAnywhere Version | 3.12 (Flask 3.0.3) |
| WSGI File Path | `/home/KhaledSoliman/mysite/flask_app.py` |
| Deployment URL |
```
https://khaledsoliman.pythonanywhere.com/khaledsoliman1599_gmail_com?x={}&y={}
```

---

## 🧪 Live Testing

| Request | Output |
|--------|--------|
| https://khaledsoliman.pythonanywhere.com/khaledsoliman1599_gmail_com?x=12&y=18 | `36` |

---

## 📤 Submission

Submitted via Discord bot using:

```
!task3 khaledsoliman1599@gmail.com https://khaledsoliman.pythonanywhere.com/khaledsoliman1599_gmail_com?x={}&y={}
```

### 🟢 Submission Status

✔ **The solution for Task 3 was accepted.**  
Assigned to: **khaledsoliman1599@gmail.com**

---

## 📎 Repository

The implementation is available at:

🔗 https://github.com/Khalodddd/data_engineering_tasks/tree/main/task3

---

## 📝 Notes

- The API correctly calculates LCM and handles invalid inputs.
- Returns results as plain numeric text (required format).
- Fully deployed online and validated.
- No additional files are included beyond what is necessary.

---

## 👤 Author

**Khaled Soliman**  
📧 `khaledsoliman1599@gmail.com`

🎯 *Task 3 completed successfully*

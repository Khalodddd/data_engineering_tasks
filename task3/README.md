```markdown
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

## ❗ Important Notes
- Only **digits** should be returned (no spaces, no newlines).
- Supports **large integers correctly** (beyond JavaScript limits).
- If invalid input → returns `NaN`.
- Development server only (Flask).
- Required for **submission to bot** using format:  
  ```
  !task3 your_email http://your_deployed_url?x={}&y={}
  ```

---

## 👤 Author

**Khaled Soliman**  
`khaledsoliman1599@gmail.com`
```

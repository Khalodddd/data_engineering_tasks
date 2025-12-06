# Task 6: Fake User Data Generator
## Khaled Soliman | khaledsoliman159@gmail.com

### Requirements Met:
✅ Web app with Flask
✅ PostgreSQL stored procedures for data generation
✅ USA and Germany locales  
✅ Seed-based reproducibility
✅ Batch generation (10 at a time)
✅ Next batch functionality
✅ Single names table with locale field
✅ 30,000+ names support
✅ Full names, addresses, coordinates, height/weight, phones, emails
✅ Uniform sphere coordinates
✅ Normal distribution for physical attributes
✅ Modular SQL functions

### How to run:
1. pip install -r requirements.txt
2. Setup PostgreSQL (see SETUP.md)
3. python app.py
4. Open http://localhost:5000

### API:
POST /generate
{"locale": "USA"|"Germany", "seed": number, "batch_size": number, "batch_index": number}

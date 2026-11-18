# Tack — campus marketplace (Flask + MySQL)

## Setup

1. Install Python 3.10+ and MySQL.
2. Create the database and tables:
   ```
   mysql -u root -p < database/schema.sql
   ```
3. Create a virtual environment and install packages:
   ```
   python -m venv venv
   venv\Scripts\activate          # Windows
   source venv/bin/activate       # Mac / Linux
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your MySQL password and a random `SECRET_KEY`.
   Optionally set `ALLOWED_EMAIL_DOMAIN` to restrict signup to your college email.
5. (Optional) Load demo data: `python database/seed.py`  (login: demo@campus.edu / demo1234)
6. Run: `python app.py` and open http://127.0.0.1:5000

## Features

- Register / log in (hashed passwords, sessions)
- Post ads with photo upload, price, condition, hostel
- Search, category chips, price/condition/hostel filters, sorting
- Listing page; seller's phone number only visible to logged-in users
- Message the seller; sellers see messages in "My listings"
- Edit, mark sold, delete your own listings

## Folder layout

```
app.py  config.py  requirements.txt
database/   schema.sql, seed.py, db.py
routes/     auth.py, listings.py, messages.py
utils/      validators.py, decorators.py
templates/  base, index, login, register, my_listings, listing_detail, 404
static/     css/style.css, js/*.js, uploads/
```

## Notes for deployment

Vercel is not suited to Flask + MySQL. Use PythonAnywhere (free MySQL) or Render + a hosted MySQL,
set `SECRET_KEY` and the DB variables there, and turn off `debug=True`.

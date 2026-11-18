"""Optional demo data.

Run from the project root AFTER creating the tables:
    python database/seed.py

Creates a demo account (demo@campus.edu / demo1234) and 9 sample listings.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from werkzeug.security import generate_password_hash

from config import Config

LISTINGS = [
    ("Engineering Mathematics (B.S. Grewal)", "Books & Notes", 350, "used", "Latest edition, light highlighting.", "Aravali Hostel"),
    ("Data Structures notes (handwritten)", "Books & Notes", 0, "used", "Complete semester notes, free to a junior.", "Nilgiri Hostel"),
    ("Hero Sprint cycle, 21 gear", "Bikes & Cycles", 3800, "used", "Rides well, new tyres last month.", "Vindhya Hostel"),
    ("Table fan (Havells, 400 mm)", "Hostel Essentials", 700, "used", "Works perfectly, 3 speeds.", "Aravali Hostel"),
    ("Study table with drawer", "Furniture", 1500, "used", "Sturdy wood, easy to carry.", "Day Scholar"),
    ("Boat Rockerz Bluetooth headphones", "Electronics", 900, "new", "Barely used, box included.", "Nilgiri Hostel"),
    ("Scientific calculator (Casio fx-991EX)", "Electronics", 650, "new", "Exam approved, with cover.", "Vindhya Hostel"),
    ("Fest pass: Tech Fest day 2", "Tickets & Passes", 200, "new", "Cannot attend, transferable.", "Aravali Hostel"),
    ("Electric kettle 1.5 L", "Hostel Essentials", 350, "used", "Auto shut-off, works fine.", "Day Scholar"),
]


def main():
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
    )
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email = %s", ("demo@campus.edu",))
    row = cur.fetchone()
    if row:
        user_id = row[0]
    else:
        cur.execute(
            "INSERT INTO users (name, email, password_hash, phone, hostel) VALUES (%s,%s,%s,%s,%s)",
            ("Demo Student", "demo@campus.edu", generate_password_hash("demo1234"), "9876543210", "Aravali Hostel"),
        )
        user_id = cur.lastrowid

    for title, category, price, cond, desc, hostel in LISTINGS:
        cur.execute(
            "INSERT INTO listings (seller_id, title, category, price, item_condition, description, hostel, phone) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (user_id, title, category, price, cond, desc, hostel, "9876543210"),
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Seeded {len(LISTINGS)} listings. Login: demo@campus.edu / demo1234")


if __name__ == "__main__":
    main()

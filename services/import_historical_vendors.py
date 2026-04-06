#import sqlite3
# from pathlib import Path
# #from datetime import datetime

# # ---- Path to your database ----
# BASE_DIR = Path(__file__).resolve().parent.parent  # parent of 'services'
# DB_PATH = BASE_DIR / "procurement.db"

# def get_connection():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn

# # ---- Historical vendor data ----
# # Fill in all your past procurement data here
# historical_data = [
#     {
#         "vendor_name": "QWE",
#         "email": "QWE@gmail.com",
#         "phone": "1234567890",
#         "project": "Project X",
#         "material": "Module",
#         "unit_price": 100,
#         "quantity": 1000,
#         "delivery_days": 15,
#         "payment_terms": "30% advance",
#         "received_date": "2025-12-01 10:00:00"
#     },
#     {
#         "vendor_name": "RTY",
#         "email": "RTY@gmail.com.com",
#         "phone": "9876543210",
#         "project": "Project Y",
#         "material": "Inverter",
#         "unit_price": 200,
#         "quantity": 5,
#         "delivery_days": 20,
#         "payment_terms": "50% advance",
#         "received_date": "2025-12-05 11:00:00"
#     }
#     # Add more historical vendors here
# ]

# # ---- Insert data into database ----
# conn = get_connection()
# cursor = conn.cursor()

# for row in historical_data:
#     # Insert vendor
#     cursor.execute("""
#         INSERT OR IGNORE INTO vendors (vendor_name, email, phone)
#         VALUES (%s, %s, %s)
#     """, (row['vendor_name'], row['email'], row['phone']))
    
#     cursor.execute("SELECT id FROM vendors WHERE vendor_name=?", (row['vendor_name'],))
#     vendor_id = cursor.fetchone()['id']

#     # Insert project
#     cursor.execute("INSERT OR IGNORE INTO projects (project_name) VALUES (%s)", (row['project'],))
#     cursor.execute("SELECT id FROM projects WHERE project_name=%s", (row['project'],))
#     project_id = cursor.fetchone()['id']

#     # Insert material
#     cursor.execute("""
#         INSERT OR IGNORE INTO materials (project_id, material_name)
#         VALUES (%s, %s)
#     """, (project_id, row['material']))
#     cursor.execute("SELECT id FROM materials WHERE project_id=%s AND material_name=%s", (project_id, row['material']))
#     material_id = cursor.fetchone()['id']

#     # Insert vendor quote
#     cursor.execute("""
#         INSERT INTO vendor_quotes
#         (material_id, vendor_id, unit_price, quantity, delivery_days, payment_terms, received_date)
#         VALUES (%s, %s, %s, %s, %s, %s, %s)
#     """, (
#         material_id,
#         vendor_id,
#         row['unit_price'],
#         row['quantity'],
#         row['delivery_days'],
#         row['payment_terms'],
#         row['received_date']
#     ))

# conn.commit()
# conn.close()
# print("Historical vendor data imported successfully!")

"""
import_historical_vendors.py

Run this ONCE to seed your PostgreSQL database with historical vendor data.
Requires DATABASE_URL set in environment:
    export DATABASE_URL="postgresql://user:password@host:port/dbname"
"""

import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set.")


def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn


# ---- Historical vendor data — expand this list as needed ----
historical_data = [
    {
        "vendor_name": "QWE",
        "email": "QWE@gmail.com",
        "phone": "1234567890",
        "project": "Project X",
        "material": "Module",
        "unit_price": 100,
        "quantity": 1000,
        "delivery_days": 15,
        "payment_terms": "30% advance",
        "received_date": "2025-12-01 10:00:00"
    },
    {
        "vendor_name": "RTY",
        "email": "RTY@gmail.com",   # fixed duplicate .com.com typo
        "phone": "9876543210",
        "project": "Project Y",
        "material": "Inverter",
        "unit_price": 200,
        "quantity": 5,
        "delivery_days": 20,
        "payment_terms": "50% advance",
        "received_date": "2025-12-05 11:00:00"
    }
    # Add more rows here
]


def run_import():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    for row in historical_data:

        # --- Vendor ---
        cursor.execute("""
            INSERT INTO vendors (vendor_name, email, phone)
            VALUES (%s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, (row["vendor_name"], row["email"], row["phone"]))

        cursor.execute(
            "SELECT id FROM vendors WHERE email = %s",
            (row["email"],)
        )
        vendor_id = cursor.fetchone()["id"]

        # --- Project ---
        cursor.execute("""
            INSERT INTO projects (project_id, project_name)
            VALUES (%s, %s)
            ON CONFLICT (project_id) DO NOTHING
        """, (row["project"], row["project"]))

        cursor.execute(
            "SELECT id FROM projects WHERE project_id = %s",
            (row["project"],)
        )
        project_id = cursor.fetchone()["id"]

        # --- RFQ master entry ---
        cursor.execute("""
            INSERT INTO rfq_master
                (project_id, material_name, quantity, rfq_date, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING rfq_id
        """, (project_id, row["material"], row["quantity"], row["received_date"], "Historical"))

        rfq_id = cursor.fetchone()["rfq_id"]

        # --- Vendor quote ---
        cursor.execute("""
            INSERT INTO vendor_quotes
                (rfq_id, vendor_name, vendor_email, unit_price,
                 delivery_time, payment_terms, email_received_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            rfq_id,
            row["vendor_name"],
            row["email"],
            row["unit_price"],
            str(row["delivery_days"]) + " days",
            row["payment_terms"],
            row["received_date"],
            "Quote Received"
        ))

    conn.commit()
    conn.close()
    print("✅ Historical vendor data imported successfully!")


if __name__ == "__main__":
    run_import()

#from db import get_connection

#def init_database():
#    conn = get_connection()
#    cursor = conn.cursor()

    # USERS
#    cursor.execute("""
#    CREATE TABLE IF NOT EXISTS users (
#        id INTEGER PRIMARY KEY AUTOINCREMENT,
#        username TEXT UNIQUE,
#        password TEXT,
#        role TEXT,
#        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#    )
#    """)

#    cursor.execute("""
#    INSERT OR IGNORE INTO users (username, password, role)
#    VALUES ('procurement', 'procure123', 'procurement')
#    """)

    # PROJECTS
    # PROJECTS
#    cursor.execute("""
#    CREATE TABLE IF NOT EXISTS projects (
#        id INTEGER PRIMARY KEY AUTOINCREMENT,
#       project_code TEXT UNIQUE,
#        project_name TEXT,
#        client TEXT,
#        location TEXT,
#        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#    )
#    """)

    # MATERIALS
#    cursor.execute("""
#    CREATE TABLE IF NOT EXISTS materials (
#        id INTEGER PRIMARY KEY AUTOINCREMENT,
#        project_id INTEGER,
#        material_name TEXT,
#        specification TEXT,
#        boq_quantity REAL,
#        status TEXT DEFAULT 'Pending'
#    )
#    """)

    # VENDORS
#    cursor.execute("""
#    CREATE TABLE IF NOT EXISTS vendors (
#        id INTEGER PRIMARY KEY AUTOINCREMENT,
#        vendor_name TEXT,
#        email TEXT,
#        phone TEXT
#    )
#    """)

    # VENDOR QUOTES
#    cursor.execute("""
#    CREATE TABLE IF NOT EXISTS vendor_quotes (
#        id INTEGER PRIMARY KEY AUTOINCREMENT,
#        material_id INTEGER,
#        vendor_id INTEGER,
#        unit_price REAL,
#        total_price REAL,
#        delivery_days INTEGER,
#        payment_terms TEXT,
#        gst TEXT,
#        received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#    )
#    """)

    # MATERIAL APPROVALS
#    cursor.execute("""
#    CREATE TABLE IF NOT EXISTS material_approvals (
#        id INTEGER PRIMARY KEY AUTOINCREMENT,
#       material_id INTEGER,
#        vendor_id INTEGER,
#        approval_token TEXT,
#        status TEXT DEFAULT 'Pending',
#        approved_at TIMESTAMP,
#        remarks TEXT
#    )
#    """)
#    cursor.execute("""
#    CREATE TABLE IF NOT EXISTS rfq_master (
#        id INTEGER PRIMARY KEY AUTOINCREMENT,
#        project_id INTEGER,
#        material_name TEXT,
#        rfq_date TEXT,
#        status TEXT
#    )
#    """)
#    cursor.execute("""
#    CREATE TABLE IF NOT EXISTS rfq_vendors (
#        id INTEGER PRIMARY KEY AUTOINCREMENT,
#        rfq_id INTEGER,
#        vendor_name TEXT,
#        vendor_email TEXT,
#        status TEXT
#    )
#    """)
#    conn.commit()
#    conn.close()

#if __name__ == "__main__":
#    init_database()
#    print("Database initialized successfully.")

# from services.db import get_connection

# conn = get_connection()
# cursor = conn.cursor()

# USERS
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT,
#     password TEXT
# )
# """)

# PROJECTS
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS projects (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     project_code TEXT UNIQUE,
#     project_name TEXT,
#     client TEXT,
#     location TEXT
# )
# """)

# # RFQ MASTER
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS rfq_master (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     project_id INTEGER,
#     material_name TEXT COLLATE NOCASE,
#     rfq_date TEXT,
#     status TEXT,
#     rfq_token TEXT
# )
# """)

# # RFQ VENDORS
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS rfq_vendors (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     rfq_id INTEGER,
#     vendor_name TEXT,
#     vendor_email TEXT,
#     status TEXT,
#     unit_price REAL,
#     delivery_time TEXT,
#     payment_terms TEXT,
#     raw_email TEXT,
#     received_date TEXT
# )
# """)

# conn.commit()
# conn.close()

# print("Database initialized successfully")
#correct

# import sqlite3

# conn = sqlite3.connect("procurement.db")
# cursor = conn.cursor()

# # =========================
# # USERS (LOGIN)
# # =========================
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT UNIQUE,
#     password TEXT
# )
# """)

# # =========================
# # PROJECTS
# # =========================
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS projects (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     project_id TEXT UNIQUE,
#     project_name TEXT
# )
# """)

# # =========================
# # RFQ MASTER
# # =========================
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS rfq_master (
#     rfq_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     project_id INTEGER,
#     material_name TEXT,
#     quantity REAL,
#     uom TEXT,
#     specification TEXT,
#     rfq_date TEXT,
#     status TEXT,
#     approval_status TEXT
# )
# """)

# # =========================
# # VENDOR QUOTES
# # =========================
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS vendor_quotes (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     rfq_id INTEGER,
#     vendor_name TEXT,
#     vendor_email TEXT,
#     unit_price REAL,
#     delivery_time TEXT,
#     payment_terms TEXT,
#     email_received_date TEXT,
#     raw_email TEXT,
#     status TEXT
# )
# """)

# # =========================
# # VENDOR APPROVALS
# # =========================
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS vendor_approvals (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     project_id INTEGER,
#     material_name TEXT,
#     vendor_name TEXT,
#     unit_price REAL,
#     delivery_time TEXT,
#     payment_terms TEXT,
#     status TEXT
# )
# """)

# conn.commit()
# conn.close()

# print("✅ Database initialized successfully")

"""
init_db.py

Run once to create all tables in your PostgreSQL database.
Requires DATABASE_URL set in environment:
    export DATABASE_URL="postgresql://user:password@host:port/dbname"
"""

import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set.")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# =========================
# USERS (LOGIN)
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# =========================
# PROJECTS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    project_id TEXT UNIQUE NOT NULL,
    project_name TEXT
)
""")

# =========================
# VENDORS (master list)
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS vendors (
    id SERIAL PRIMARY KEY,
    vendor_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT
)
""")

# =========================
# RFQ MASTER
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS rfq_master (
    rfq_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    material_name TEXT,
    quantity REAL,
    uom TEXT,
    specification TEXT,
    rfq_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    approval_status TEXT
)
""")

# =========================
# VENDOR QUOTES
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS vendor_quotes (
    id SERIAL PRIMARY KEY,
    rfq_id INTEGER REFERENCES rfq_master(rfq_id),
    vendor_name TEXT,
    vendor_email TEXT,
    unit_price REAL,
    quantity REAL DEFAULT 0,
    delivery_time TEXT,
    payment_terms TEXT,
    email_received_date TIMESTAMP,
    raw_email TEXT,
    status TEXT
)
""")

# =========================
# VENDOR APPROVALS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS vendor_approvals (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    material_name TEXT,
    vendor_name TEXT,
    unit_price REAL,
    delivery_time TEXT,
    payment_terms TEXT,
    status TEXT DEFAULT 'Pending'
)
""")

# =========================
# DEFAULT ADMIN USER
# =========================
cursor.execute("""
INSERT INTO users (username, password)
VALUES ('admin', 'admin123')
ON CONFLICT (username) DO NOTHING
""")

conn.commit()
conn.close()

print("✅ PostgreSQL database initialized successfully")
print("   Default login: admin / admin123  (change this in production!)")
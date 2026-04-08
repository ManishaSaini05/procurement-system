#import sqlite3
#from pathlib import Path

#BASE_DIR = Path(__file__).resolve().parent.parent
#DB_PATH = BASE_DIR / "procurement.db"

#def get_connection():
#    conn = sqlite3.connect(DB_PATH)
#    conn.row_factory = sqlite3.Row
#    return conn

#import sqlite3

# def get_connection():
#     conn = sqlite3.connect("procurement.db",check_same_thread=False)
#     conn.row_factory = sqlite3.Row
#     return conn
# import psycopg2
# import psycopg2.extras
# import streamlit as st


# def get_connection():
#     conn = psycopg2.connect(st.secrets["DATABASE_URL"])
#     return conn


# def get_cursor():
#     conn = get_connection()
#     cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#     return conn, cursor

# New version #

import psycopg2
import psycopg2.extras
import streamlit as st


def get_connection():
    conn = psycopg2.connect(st.secrets["DATABASE_URL"])
    return conn


def get_cursor():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return conn, cursor
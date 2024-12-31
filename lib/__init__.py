# lib/config.py
import sqlite3

CONN = sqlite3.connect('rental_management.db')
CONN.execute("PRAGMA foreign_keys = ON;")
CURSOR = CONN.cursor()

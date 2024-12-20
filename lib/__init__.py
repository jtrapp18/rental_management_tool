# lib/config.py
import sqlite3

CONN = sqlite3.connect('rental_management.db')
CURSOR = CONN.cursor()

import sqlite3
import pprint

conn = sqlite3.connect('woundtrack.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- PATIENTS ---")
for row in cursor.execute('SELECT * FROM patients').fetchall():
    print(dict(row))

print("\n--- WOUNDS ---")
for row in cursor.execute('SELECT * FROM wounds').fetchall():
    print(dict(row))

print("\n--- ASSESSMENTS ---")
for row in cursor.execute('SELECT id, wound_id, day, notes FROM wound_assessments').fetchall():
    print(dict(row))

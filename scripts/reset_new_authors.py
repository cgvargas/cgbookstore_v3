import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'new_authors_%'")
tables = cursor.fetchall()

print(f"Found {len(tables)} tables for 'new_authors'.")

for table in tables:
    table_name = table[0]
    print(f"Dropping table {table_name}...")
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

conn.commit()
conn.close()
print("Finished dropping new_authors tables.")

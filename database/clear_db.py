import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'users.db')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Delete all rows
c.execute('DELETE FROM users')

# Optionally, reset AUTOINCREMENT counter
c.execute('DELETE FROM sqlite_sequence WHERE name="users"')

conn.commit()
conn.close()

print("All user data cleared, table structure remains.")
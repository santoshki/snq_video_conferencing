import os
import sqlite3
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(c.fetchall())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'users.db')

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()


    # Fetch all records
    c.execute("SELECT id, username, email FROM users")
    users = c.fetchall()  # Returns a list of tuples
    emails = [row[2] for row in users]
    for email_id in emails:
        print(email_id)

    conn.close()
    return users


# Example usage
for user in get_all_users():
    print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
from werkzeug.security import generate_password_hash
import sqlite3


def user_exists(email):
    try:
         conn = sqlite3.connect('C:\\Users\\santo\\PycharmProjects\\snq_video_conferencing\\database\\users.db')
         c = conn.cursor()
         c.execute("SELECT email FROM users")
         existing_emails = [row[0].strip().lower() for row in c.fetchall()]
         print("existing emails:", existing_emails)
         if email in existing_emails:
             conn.close()
             return True
         else:
            return False
    except Exception as e:
        raise e


def add_user_accounts(username, password, email):
    try:
         hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
         conn = sqlite3.connect('C:\\Users\\santo\\PycharmProjects\\snq_video_conferencing\\database\\users.db')
         c = conn.cursor()
         c.execute('''
         INSERT INTO users (username, email, password)
         VALUES (?, ?, ?)
         ''', (username, email, hashed_password))

         conn.commit()
         conn.close()

         return True, "User Account created successfully!"
    except Exception as e:
         raise e
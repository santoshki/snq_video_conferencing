import sqlite3


def create_users_db():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()
        print("Users database created successfully!")
    except Exception as e:
        raise e


if __name__ == '__main__':
    create_users_db()
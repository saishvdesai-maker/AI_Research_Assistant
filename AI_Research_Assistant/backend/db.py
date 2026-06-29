import sqlite3

DB_NAME = "app.db"


def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        approved INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


init_db()
import sqlite3
from datetime import datetime


conn = sqlite3.connect(
    "research.db",
    check_same_thread=False
)


cursor = conn.cursor()



cursor.execute("""
CREATE TABLE IF NOT EXISTS chats(

id INTEGER PRIMARY KEY AUTOINCREMENT,

question TEXT,

answer TEXT,

date TEXT

)
""")


conn.commit()



def save_chat(question,answer):

    cursor.execute(

        "INSERT INTO chats(question,answer,date) VALUES (?,?,?)",

        (
            question,
            answer,
            str(datetime.now())
        )

    )

    conn.commit()



def get_chats():

    cursor.execute(
        "SELECT * FROM chats ORDER BY id DESC"
    )

    return cursor.fetchall()
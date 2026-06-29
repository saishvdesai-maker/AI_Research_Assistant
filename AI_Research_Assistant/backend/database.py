import sqlite3


connection = sqlite3.connect(
    "research.db",
    check_same_thread=False
)

cursor = connection.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS papers(

id INTEGER PRIMARY KEY AUTOINCREMENT,

name TEXT,

date TEXT

)
""")


connection.commit()



def add_paper(name,date):

    cursor.execute(
        "INSERT INTO papers(name,date) VALUES (?,?)",
        (name,date)
    )

    connection.commit()



def get_papers():

    cursor.execute(
        "SELECT * FROM papers"
    )

    return cursor.fetchall()



def delete_paper(id):

    cursor.execute(
        "DELETE FROM papers WHERE id=?",
        (id,)
    )

    connection.commit()
from backend.db import connect


def create_user(username, password):
    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (username, password, approved) VALUES (?, ?, 0)",
            (username, password)
        )
        conn.commit()
    except:
        pass

    conn.close()


def login_user(username, password):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, approved FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cur.fetchone()
    conn.close()

    if not user:
        return None

    if user[1] == 0:
        return "not_approved"

    return user


def approve_user(username):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET approved=1 WHERE username=?",
        (username,)
    )

    conn.commit()
    conn.close()


def list_users():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT id, username, approved FROM users")
    data = cur.fetchall()

    conn.close()
    return data
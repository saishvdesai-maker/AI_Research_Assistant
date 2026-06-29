from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt

import sqlite3
import shutil
import os
import numpy as np
from dotenv import load_dotenv

from pypdf import PdfReader
from openai import OpenAI

# ----------------------------
# ENV LOAD
# ----------------------------
load_dotenv()

app = FastAPI()

# ----------------------------
# STATIC FRONTEND SAFE
# ----------------------------
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def home():
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    return {"message": "AI Research Assistant API Running"}


# ----------------------------
# DATABASE
# ----------------------------
DB = "app.db"


def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        approved INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        question TEXT,
        answer TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ----------------------------
# AUTH
# ----------------------------
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_token(username: str):
    return jwt.encode({"sub": username}, SECRET_KEY, algorithm=ALGORITHM)


def get_user(token: str = Depends(oauth2_scheme)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return data["sub"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


class User(BaseModel):
    username: str
    password: str


# ----------------------------
# LAZY MODEL (FIX MEMORY CRASH)
# ----------------------------


# ----------------------------
# OPENAI SAFE INIT
# ----------------------------
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


# ----------------------------
# STORAGE
# ----------------------------
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

pdf_store = {}
current_pdf = None


# ----------------------------
# ROUTES
# ----------------------------
@app.post("/register")
def register(user: User):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        (user.username, user.password)
    )

    conn.commit()
    conn.close()

    return {"message": "waiting approval"}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT password,approved FROM users WHERE username=?",
        (form_data.username,)
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        return {"message": "not found"}

    if row[0] != form_data.password:
        return {"message": "wrong password"}

    if row[1] == 0:
        return {"message": "not approved"}

    return {
        "access_token": create_token(form_data.username),
        "token_type": "bearer"
    }


@app.post("/admin/approve")
def approve(username: str):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("UPDATE users SET approved=1 WHERE username=?", (username,))

    conn.commit()
    conn.close()

    return {"message": "approved"}


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    global current_pdf

    path = os.path.join(UPLOAD_DIR, file.filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    reader = PdfReader(path)

    chunks = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        chunks.append({"text": text, "page": i + 1})

    


embeddings = None

    pdf_store[file.filename] = {
        "chunks": chunks,
        "embeddings": embeddings
    }

    current_pdf = file.filename

    return {"message": "uploaded"}
@app.get("/ask")
def ask(q: str, username: str = Depends(get_user)):

    if current_pdf is None:
        return {"error": "No PDF uploaded"}

    data = pdf_store[current_pdf]

    context = ""

for chunk in data["chunks"][:3]:
    context += chunk["text"] + "\n"
    

    prompt = f"""
Use this PDF:
{context}

Question:
{q}

Answer:
"""

    if client:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
    else:
        answer = "OPENAI_API_KEY not set"

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO chats(username,question,answer) VALUES(?,?,?)",
        (username, q, answer)
    )

    conn.commit()
    conn.close()

    return {"answer": answer}


@app.get("/dashboard")
def dashboard(username: str = Depends(get_user)):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM chats WHERE username=?",
        (username,)
    )

    total = cur.fetchone()[0]

    conn.close()

    return {
        "user": username,
        "questions": total
    }
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt

import sqlite3
import shutil
import os

from dotenv import load_dotenv
from pypdf import PdfReader
from openai import OpenAI

load_dotenv()

app = FastAPI()

if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def home():
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")

    return {"message": "AI Research Assistant API Running"}


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

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_token(username):
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


client = None
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

pdf_store = {}


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
        "SELECT username,password,approved FROM users WHERE username=?",
        (form_data.username,)
    )

    user = cur.fetchone()
    conn.close()

    if not user:
        raise HTTPException(404, "User not found")

    if user[1] != form_data.password:
        raise HTTPException(401, "Wrong password")

    if user[2] == 0:
        raise HTTPException(403, "Account waiting approval")

    return {
        "access_token": create_token(user[0]),
        "token_type": "bearer"
    }


@app.post("/approve/{username}")
def approve_user(username: str):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET approved=1 WHERE username=?",
        (username,)
    )

    conn.commit()
    conn.close()

    return {"message": "approved"}


@app.post("/upload")
def upload_pdf(file: UploadFile = File(...), username: str = Depends(get_user)):
    path = os.path.join(UPLOAD_DIR, file.filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    reader = PdfReader(path)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    pdf_store[username] = text

    return {"message": "PDF uploaded"}


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask(data: Question, username: str = Depends(get_user)):

    pdf_text = pdf_store.get(username, "")

    prompt = f"""
Use this PDF:
{pdf_text[:8000]}

Question:
{data.question}
"""

    if client:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )
          
    answer = response.choices[0].message.content
    
    answer = "OpenAI key missing"

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO chats(username,question,answer) VALUES(?,?,?)",
        (username, data.question, answer)
    )

    conn.commit()
    conn.close()

    return {"answer": answer}


@app.get("/history")
def history(username: str = Depends(get_user)):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT question,answer FROM chats WHERE username=?",
        (username,)
    )

    rows = cur.fetchall()
    conn.close()

    return rows

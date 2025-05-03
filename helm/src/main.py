from fastapi import FastAPI
import os
import psycopg2

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "")
DB_NAME = os.getenv("DB_NAME", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASS = os.getenv("DB_PASSWORD", "")

@app.on_event("startup")
def init_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.get("/")
def show_env():
    return {
        "env": os.getenv("ENV_NAME"),
        "location": os.getenv("LOCATION"),
        "version": os.getenv("VERSION"),
        "db_password": DB_PASS,
        "pod": os.getenv("HOSTNAME", "unknown")
    }

@app.post("/add/{name}")
def add_item(name: str):
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO items(name) VALUES (%s)", (name,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok", "item": name}

@app.get("/list")
def list_items():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM items")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": row[0], "name": row[1]} for row in results]

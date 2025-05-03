from fastapi import FastAPI
import sqlite3

app = FastAPI()

@app.get("/")
def list_fruits():
    conn = sqlite3.connect('/data/fruits.db')
    cursor = conn.execute("SELECT name, amount FROM fruits")
    fruits = [{"fruit": name, "amount": amount} for name, amount in cursor.fetchall()]
    conn.close()
    return {"fruits": fruits}

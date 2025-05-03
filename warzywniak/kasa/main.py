from fastapi import FastAPI
import sqlite3
import socket

app = FastAPI()
pod_name = socket.gethostname()

@app.on_event("startup")
def startup_event():
    conn = sqlite3.connect('/data/fruits.db')
    conn.execute('CREATE TABLE IF NOT EXISTS fruits (name TEXT PRIMARY KEY, amount INTEGER)')
    conn.commit()
    conn.close()

@app.get("/add/{fruit}/{amount}")
def add_fruit(fruit: str, amount: int):
    conn = sqlite3.connect('/data/fruits.db')
    conn.execute("INSERT INTO fruits(name, amount) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET amount=amount+?", (fruit, amount, amount))
    conn.commit()
    conn.close()
    return {"status": "added", "fruit": fruit, "amount": amount}

@app.get("/subtract/{fruit}/{amount}")
def subtract_fruit(fruit: str, amount: int):
    conn = sqlite3.connect('/data/fruits.db')
    conn.execute("UPDATE fruits SET amount = amount - ? WHERE name = ?", (amount, fruit))
    conn.commit()
    conn.close()
    return {"status": "subtracted", "fruit": fruit, "amount": amount}

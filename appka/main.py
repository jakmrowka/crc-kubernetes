from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import time

print("⏳ Aplikacja startuje... czekam 15 sekund")
time.sleep(15)
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Kubernetes demo - działa!"}

@app.get("/health")
def health():
    return JSONResponse(status_code=200, content={"status": "OK"})

@app.get("/config")
def config():
    config_var = os.getenv("MY_CONFIG_VAR", "brak configmapy")
    secret_var = os.getenv("MY_SECRET_VAR", "brak sekretu")
    return {"config_var": config_var, "secret_var": secret_var}

@app.get("/config-file")
def config_file():
    try:
        with open("/etc/appconfig/config_var", "r") as f:
            file_value = f.read().strip()
    except Exception:
        file_value = "nie udało się odczytać pliku"

    return {"file_value": file_value}
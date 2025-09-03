from fastapi import FastAPI
from time import time

app = FastAPI(title="Telegram Gym Coach Bot API", version="0.1.0")

@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "ts": time()}

@app.get("/")
def root() -> dict:
    return {"app": "telegram-gym-coach-bot", "ok": True}
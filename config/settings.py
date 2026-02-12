import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
CLIENT_ID = os.getenv("CLIENT_ID")


# ---- HARD FAILS (system cannot run) ----
if not ACCESS_TOKEN:
    raise RuntimeError("ACCESS_TOKEN missing")

if not CLIENT_ID:
    raise RuntimeError("CLIENT_ID missing")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL missing")

# ---- SOFT FAILS (system can still run) ----
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("[WARNING] Telegram disabled — token/chat_id missing")
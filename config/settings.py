import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# TELEGRAM CONFIGURATION
# ==========================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ==========================================================
# SMART API CONFIGURATION
# ==========================================================

CLIENT_ID = os.getenv("CLIENT_ID")
PASSWORD = os.getenv("PASSWORD")
API_KEY = os.getenv("API_KEY")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# ==========================================================
# DATABASE
# ==========================================================

DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")

# =====================================================
# STORAGE
# =====================================================
local_storage = os.getenv("LOCAL_STORAGE", "False").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL")


# ==========================================================
# HARD FAILS
# These are mandatory for the application to start.
# ==========================================================

if not CLIENT_ID:
    raise RuntimeError(
        "[CONFIG ERROR] CLIENT_ID is missing. Please add CLIENT_ID to your .env file."
    )

if not PASSWORD:
    raise RuntimeError(
        "[CONFIG ERROR] PASSWORD is missing. Please add PASSWORD to your .env file."
    )

if not API_KEY:
    raise RuntimeError(
        "[CONFIG ERROR] API_KEY is missing. Please add API_KEY to your .env file."
    )

if not TOTP_SECRET:
    raise RuntimeError(
        "[CONFIG ERROR] TOTP_SECRET is missing. Please add TOTP_SECRET to your .env file."
    )

# if not DATABASE_URL:
#     raise RuntimeError(
#         "[CONFIG ERROR] DATABASE_URL is missing. Please add DATABASE_URL to your .env file."
#     )


# ==========================================================
# SOFT FAILS
# The application can continue without these.
# ==========================================================

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print(
        "[WARNING] Telegram notifications are disabled "
        "(TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not found)."
    )
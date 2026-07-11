# Singleton auth object



# =========================================================
# AUTH SINGLETON
# =========================================================
#
# Responsibility:
# - Create a single AuthManager instance
# - Share it across the entire application
#
# Every module imports:
#
# from broker_websocket.auth.auth import auth
#
# =========================================================

import os
from dotenv import load_dotenv

from broker_websocket.auth.auth_manager import AuthManager

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

# =========================================================
# CREATE SINGLE AUTH INSTANCE
# =========================================================

auth = AuthManager(

    api_key=os.getenv("API_KEY"),

    client_id=os.getenv("CLIENT_ID"),

    password=os.getenv("PASSWORD"),

    totp_secret=os.getenv("TOTP_SECRET")

)
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



from broker_websocket.auth.auth_manager import AuthManager
from config.settings import CLIENT_ID,PASSWORD,API_KEY,TOTP_SECRET


# =========================================================
# CREATE SINGLE AUTH INSTANCE
# =========================================================

auth = AuthManager(

    api_key=API_KEY,
    client_id=CLIENT_ID,
    password= PASSWORD,
    totp_secret= TOTP_SECRET

)


import base64
from SmartApi import SmartConnect
import pyotp
import json
import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into os.environ
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class SmartApiAuthManager:
    def __init__(self, api_key, client_id, password, totp_secret, token_file="tokens.json"):
        """
        Initialize the Auth Manager.
        :param api_key: Angel One API Key
        :param client_id: Client ID (User ID)
        :param password: Trading Password
        :param totp_secret: The TOTP secret key (from QR code)
        :param token_file: Path to store tokens persistently
        """
        self.api_key = api_key
        self.client_id = client_id
        self.password = password
        self.totp_secret = totp_secret
        self.token_file = token_file
        
        # Initialize SmartConnect
        self.smart_api = SmartConnect(api_key=self.api_key)
        
        # Load existing tokens if available
        self._load_tokens()

    # ------------------------------------------------------------------
    # ⭐ PUBLIC INTERFACE (Only these 3 methods should be called externally)
    # ------------------------------------------------------------------

    def get_access_token(self):
        """
        Single entry point for obtaining a valid JWT.
        Handles: New Login -> Check Expiry -> Refresh -> Re-Login (if refresh fails)
        """
        # 1. Do we have an access token?
        if not self.smart_api.access_token:
            return self._login()

        # 2. Is JWT expired?
        if self._is_token_expired():
            try:
                # 3. Refresh JWT
                return self._refresh()
            except Exception:
                # 4. Refresh Failed -> Login Again
                print("⚠️ Refresh failed. Performing full login...")
                return self._login()
        
        # 5. Return valid JWT
        return self.smart_api.access_token

    def get_feed_token(self):
        """
        Returns the latest feed token.
        Ensures access token is valid first (which updates feed token internally).
        """
        # Ensure we have a valid session (which updates feed_token internally)
        self.get_access_token()
        return self.smart_api.feed_token

    def logout(self):
        """Terminate the session and clear stored tokens."""
        try:
            self.smart_api.terminateSession(self.client_id)
        except Exception:
            pass # Ignore errors during logout
        
        # Clear local state
        self.smart_api.setAccessToken("")
        self.smart_api.setRefreshToken("")
        self.smart_api.setFeedToken("")
        self._store_tokens(jwt="", refresh="", feed="")

    # ------------------------------------------------------------------
    # 🔒 INTERNAL HELPERS (Private methods)
    # ------------------------------------------------------------------

    def _login(self):
        """
        Performs a full login using Credentials + TOTP.
        Updates internal state and storage.
        """
        try:
            # Generate current TOTP
            totp = pyotp.TOTP(self.totp_secret).now()
            
            # Call generateSession
            data = self.smart_api.generateSession(self.client_id, self.password, totp)
            
            if not data.get('status'):
                raise Exception(f"Login failed: {data.get('message')}")
            
            # Extract tokens (generateSession sets them internally, but we ensure storage)
            jwt_token = data['data']['jwtToken']
            refresh_token = data['data']['refreshToken']
            feed_token = self.smart_api.getfeedToken() # Fetch explicitly
            
            # Store persistently
            self._store_tokens(jwt_token, refresh_token, feed_token)
            
            return jwt_token
            
        except Exception as e:
            print(f"❌ Login Error: {e}")
            raise

    def _refresh(self):
        """
        Refreshes the JWT using the Refresh Token.
        Updates internal state and storage.
        """
        if not self.smart_api.refresh_token:
            raise Exception("No refresh token available.")
            
        # Use generateToken(refreshToken) as it's more direct than renewAccessToken()
        # which sometimes requires a valid access token to work correctly.
        response = self.smart_api.generateToken(self.smart_api.refresh_token)
        
        if not response.get('status'):
            raise Exception(f"Refresh failed: {response.get('message')}")
        
        # Extract new tokens
        new_jwt = response['data']['jwtToken']
        new_feed = response['data'].get('feedToken', self.smart_api.feed_token)
        # Note: generateToken usually doesn't return a NEW refresh token in some SDK versions,
        # but the API docs say it rotates. We keep the existing one if not returned.
        new_refresh = response['data'].get('refreshToken', self.smart_api.refresh_token)
        
        # Update SDK state explicitly just in case
        self.smart_api.setAccessToken(new_jwt)
        self.smart_api.setFeedToken(new_feed)
        self.smart_api.setRefreshToken(new_refresh)
        
        # Store persistently
        self._store_tokens(new_jwt, new_refresh, new_feed)
        
        return new_jwt

    def _is_token_expired(self):
        """
        Checks if the current JWT is expired.
        Returns: True if expired or missing, False otherwise.
        """
        token = self.smart_api.access_token
        if not token:
            return True
            
        try:
            # Manual decode to check 'exp' without verifying signature
            # Format: header.payload.signature
            payload = token.split('.')[1]
            # Fix padding
            payload += '=' * (-len(payload) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            
            exp = decoded.get('exp')
            if not exp:
                return False # No expiry claim = never expires (rare)
            
            # Compare with current time (exp is in seconds)
            return datetime.utcnow().timestamp() >= exp
            
        except Exception:
            # If decoding fails, treat as expired to force re-login
            return True

    def _store_tokens(self, jwt, refresh, feed):
        """Saves tokens to a local JSON file."""
        data = {
            "jwtToken": jwt,
            "refreshToken": refresh,
            "feedToken": feed,
            "timestamp": datetime.utcnow().isoformat()
        }
        try:
            with open(self.token_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"⚠️ Failed to save tokens: {e}")

    def _load_tokens(self):
        """Loads tokens from the local JSON file into SmartConnect."""
        if not os.path.exists(self.token_file):
            return
            
        try:
            with open(self.token_file, 'r') as f:
                data = json.load(f)
            
            jwt = data.get("jwtToken")
            refresh = data.get("refreshToken")
            feed = data.get("feedToken")
            
            if jwt:
                self.smart_api.setAccessToken(jwt)
            if refresh:
                self.smart_api.setRefreshToken(refresh)
            if feed:
                self.smart_api.setFeedToken(feed)
                
        except Exception as e:
            print(f"⚠️ Failed to load tokens: {e}")

    def get_api_key(self):
        """Returns the API Key."""
        return self.api_key
    
    def get_client_id(self):
        """Returns the Client ID."""
        return self.client_id
    
# ----------------------------------------------------------------------
# USAGE EXAMPLE
# ----------------------------------------------------------------------
# Configuration
API_KEY = os.getenv('API_KEY')
CLIENT_ID = os.getenv('CLIENT_ID')
PASSWORD = os.getenv('PASSWORD')
TOTP_SECRET = os.getenv('TOTP_SECRET')

# Initialize Manager
auth = SmartApiAuthManager(
    api_key=API_KEY,
    client_id=CLIENT_ID,
    password=PASSWORD,
    totp_secret=TOTP_SECRET
)

# if __name__ == "__main__":
    
    
#     # 1. Get Access Token (Handles login/refresh automatically)
#     try:
#         token = auth.get_access_token()
#         print(f"✅ Ready to trade. Access Token: {token}")
        
#         # 2. Get Feed Token (Ensures session is valid)
#         feed_token = auth.get_feed_token()
#         print(f"📡 Feed Token: {feed_token}")
        
#         # 3. Use tokens in your OrderManager or WebSocket
#         # order_manager.place_order(token=token, ...)
        
#     except Exception as e:
#         print(f"🚫 Critical Auth Failure: {e}")   
# =========================================================
# AUTH MANAGER
# =========================================================
#
# Responsibility:
# - Login
# - Refresh JWT
# - Return valid access token
# - Return feed token
# - Logout
#
# It DOES NOT:
# ❌ Store JSON
# ❌ Decode JWT
#
# =========================================================

import threading
import pyotp
import time
from SmartApi import SmartConnect

from broker_websocket.auth.token_storage import TokenStorage
from broker_websocket.auth.jwt_utils import JWTUtils


class AuthManager:

    def __init__(
        self,
        api_key,
        client_id,
        password,
        totp_secret
    ):

        self.api_key = api_key
        self.client_id = client_id
        self.password = password
        self.totp_secret = totp_secret

        self.smart_api = SmartConnect(
            api_key=self.api_key
        )

        self.storage = TokenStorage()

        # Prevent multiple threads from refreshing simultaneously
        self.lock = threading.Lock()

        self._restore_session()

    # =====================================================
    # RESTORE PREVIOUS SESSION
    # =====================================================

    def _restore_session(self):

        data = self.storage.load()

        if not data:

            print("[AUTH] No saved session found.")

            return

        print("[AUTH] Loading saved session...")

        self.smart_api.setAccessToken(
            data.get("jwtToken")
        )

        self.smart_api.setRefreshToken(
            data.get("refreshToken")
        )

        self.smart_api.setFeedToken(
            data.get("feedToken")
        )

        print("[AUTH] Session loaded successfully.")
    # =====================================================
    # ACCESS TOKEN
    # =====================================================

    def get_access_token(self):

        with self.lock:

            print("[AUTH] Checking session.....")
            jwt = self.smart_api.access_token
            session = self.storage.load()

            expires_at = None
            if session:
                expires_at = session.get("expireAt")

            # -------------------------------
            # No JWT → Login
            # -------------------------------

            if not jwt:
                
                print("[AUTH] No session found.")
                print("[AUTH] Performing fresh login...")
                return self._login()

            # -------------------------------
            # JWT Expired
            # -------------------------------

            if expires_at is None or time.time() >= expires_at:

                print("[AUTH] Session restored.")
                print("[AUTH] JWT expired.")

                try:

                    return self._refresh()

                except Exception:

                    print(
                        "[AUTH] Refresh failed."
                    )

                    print("[AUTH] Performing fresh login...")

                    return self._login()

            # -------------------------------
            # JWT Valid
            # -------------------------------

            print("[AUTH] Session restored.")
            print("[AUTH] JWT is Valid.")
            return jwt

    # =====================================================
    # GET FEED TOKEN
    # =====================================================

    def get_feed_token(self):
        """
        Returns the current Feed Token.

        Assumes get_access_token() has already been called
        during system startup.
        """

        return self.smart_api.feed_token

    # =====================================================
    # LOGIN
    # =====================================================

    def _login(self):

        print("[AUTH] Logging in...")

        totp = pyotp.TOTP(
            self.totp_secret
        ).now()

        response = self.smart_api.generateSession(

            self.client_id,

            self.password,

            totp
        )

        if not response.get("status"):

            raise Exception(
                response.get("message")
            )

        jwt = response["data"]["jwtToken"]

        refresh = response["data"]["refreshToken"]

        feed = self.smart_api.getfeedToken()

        self.smart_api.setFeedToken(feed)

        expires = JWTUtils.get_expiry(jwt)

        self.storage.save(

            jwt=jwt,

            refresh=refresh,

            feed=feed,

            expires_at=expires

        )

        print("[AUTH] Login successful.")

        return jwt

    # =====================================================
    # REFRESH
    # =====================================================

    def _refresh(self):

        print("[AUTH] Refreshing JWT...")

        response = self.smart_api.generateToken(

            self.smart_api.refresh_token

        )

        if not response.get("status"):

            raise Exception(
                response.get("message")
            )

        jwt = response["data"]["jwtToken"]

        refresh = response["data"].get(

            "refreshToken",

            self.smart_api.refresh_token

        )

        feed = response["data"].get(

            "feedToken",

            self.smart_api.feed_token

        )

        self.smart_api.setAccessToken(jwt)

        self.smart_api.setRefreshToken(refresh)

        self.smart_api.setFeedToken(feed)

        expires = JWTUtils.get_expiry(jwt)

        self.storage.save(

            jwt=jwt,

            refresh=refresh,

            feed=feed,

            expires_at=expires

        )

        print("[AUTH] Refresh successful.")

        return jwt

    # =====================================================
    # LOGOUT
    # =====================================================

    def logout(self):

        try:

            self.smart_api.terminateSession(
                self.client_id
            )

        except Exception:

            pass

        self.storage.clear()

        self.smart_api.setAccessToken("")

        self.smart_api.setRefreshToken("")

        self.smart_api.setFeedToken("")

        print("[AUTH] Logged out.")

    # =====================================================
    # GETTERS
    # =====================================================

    def get_api_key(self):

        return self.api_key

    def get_client_id(self):

        return self.client_id
    

    # =====================================================
    # GET SESSION
    # =====================================================

    def get_session(self):
        """
        Returns a complete authenticated session.

        Ensures JWT is valid before returning
        broker credentials.
        """

        # Make sure authentication is valid
        self.get_access_token()

        return {

            "auth_token": self.smart_api.access_token,

            "feed_token": self.smart_api.feed_token,

            "api_key": self.api_key,

            "client_id": self.client_id

        }
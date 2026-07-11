# Read & Write tokens.json

import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

class TokenStorage:

    def __init__(self, file_path="broker_websocket/auth/tokens.json"):

        self.file_path = file_path

    # =====================================================
    # LOAD TOKENS
    # =====================================================

    def load(self):

        if not os.path.exists(self.file_path):
            return None

        try:

            with open(self.file_path, "r") as file:
                return json.load(file)

        except Exception:

            return None

    # =====================================================
    # SAVE TOKENS
    # =====================================================

    def save(
        self,
        jwt,
        refresh,
        feed,
        expires_at
    ):

        # Current IST time
        updated_time = datetime.now(
            ZoneInfo("Asia/Kolkata")
        )

        # Expiry time in IST
        expiry_time = datetime.fromtimestamp(
            expires_at,
            ZoneInfo("Asia/Kolkata")
        )

        data = {

            # Tokens
            "jwtToken": jwt,

            "refreshToken": refresh,

            "feedToken": feed,

            # Machine-readable expiry
            "expiresAt": expires_at,

            # Human-readable expiry
            "expiresAtIST": expiry_time.strftime(
                "%d-%m-%Y %I:%M:%S %p"
            ),

            # Last authentication time
            "lastAuthentication": updated_time.strftime(
                "%d-%m-%Y %I:%M:%S %p"
            )

        }

        with open(
            self.file_path,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    # =====================================================
    # CLEAR TOKENS
    # =====================================================

    def clear(self):

        if os.path.exists(self.file_path):

            os.remove(self.file_path)


    def get_expiry(self):

        data = self.load()

        if not data:
            return None
        
        return data.get("expiresAt")
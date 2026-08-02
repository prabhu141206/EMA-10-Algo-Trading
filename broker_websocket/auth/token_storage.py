# Read & Write Tokens

import json
import os
import redis

from datetime import datetime
from zoneinfo import ZoneInfo

from config.settings import LOCAL_STORAGE, REDIS_URL


class TokenStorage:

    def __init__(
        self,
        file_path="broker_websocket/auth/tokens.json"
    ):

        self.file_path = file_path

        self.local_storage = LOCAL_STORAGE

        self.redis = None

        if not self.local_storage:

            self.redis = redis.from_url(
                REDIS_URL,
                decode_responses=True
            )

    # =====================================================
    # LOAD TOKENS
    # =====================================================

    def load(self):

        # ---------------------------------------------
        # Redis Storage
        # ---------------------------------------------

        if not self.local_storage:

            data = self.redis.get("smart_api_tokens")

            if data:

                return json.loads(data)

            return None

        # ---------------------------------------------
        # Local Storage
        # ---------------------------------------------

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

        # ---------------------------------------------
        # Redis Storage
        # ---------------------------------------------

        if not self.local_storage:

            self.redis.set(
                "smart_api_tokens",
                json.dumps(data)
            )

            return

        # ---------------------------------------------
        # Local Storage
        # ---------------------------------------------

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

        # ---------------------------------------------
        # Redis Storage
        # ---------------------------------------------

        if not self.local_storage:

            self.redis.delete("smart_api_tokens")

            return

        # ---------------------------------------------
        # Local Storage
        # ---------------------------------------------

        if os.path.exists(self.file_path):

            os.remove(self.file_path)

    # =====================================================
    # GET TOKEN EXPIRY
    # =====================================================

    def get_expiry(self):

        data = self.load()

        if not data:

            return None

        return data.get("expiresAt")
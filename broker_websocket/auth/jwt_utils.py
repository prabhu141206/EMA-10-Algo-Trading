# =========================================================
# JWT UTILITIES
# =========================================================
#
# Responsibility:
# - Decode JWT payload
# - Extract expiry time
# - Check whether JWT is expired
#
# =========================================================

import base64
import json
from datetime import datetime


class JWTUtils:

    # =====================================================
    # GET JWT EXPIRY
    # =====================================================

    @staticmethod
    def get_expiry(jwt_token):

        if not jwt_token:
            return None

        try:

            payload = jwt_token.split(".")[1]

            # Fix Base64 padding
            payload += "=" * (-len(payload) % 4)

            decoded = json.loads(
                base64.urlsafe_b64decode(payload)
            )

            return decoded.get("exp")

        except Exception:

            return None

    # =====================================================
    # CHECK EXPIRY
    # =====================================================

    # @staticmethod
    # def is_expired(jwt_token):

    #     expiry = JWTUtils.get_expiry(jwt_token)

    #     if expiry is None:
    #         return True

    #     current_time = datetime.utcnow().timestamp()

    #     return current_time >= expiry
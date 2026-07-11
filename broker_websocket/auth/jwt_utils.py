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


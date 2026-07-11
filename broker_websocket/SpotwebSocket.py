# =========================================================
# SPOT WEBSOCKET
# =========================================================
#
# Responsibility:
# - Connect to SmartAPI
# - Subscribe to NIFTY Spot
# - Forward ticks to TickHandler
#
# =========================================================

from SmartApi.smartWebSocketV2 import SmartWebSocketV2
# from auth import auth
from logzero import logger


class SpotWebSocket:

    def __init__(self, session, tick_handler):

        self.session = session
        self.tick_handler = tick_handler

        self.sws = None

        self.connected = False

        self.correlation_id = "spot_ws"

        # Quote Mode
        self.mode = 1
        self.action = 1

        # NIFTY INDEX
        self.token_list = [
            {
                "exchangeType": 1,
                "tokens": ["99926000"]
            }
        ]

    # =====================================================
    # CONNECT
    # =====================================================

    def connect(self):

        """Initialize and start the WebSocket connection."""
        AUTH_TOKEN = self.session["auth_token"]
        API_KEY = self.session["api_key"]
        CLIENT_CODE = self.session["client_id"]
        FEED_TOKEN = self.session["feed_token"]

        # Initialize SmartWebSocketV2
        self.sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)

        self._setup_callbacks()

        print(
            "[SPOT WS] Connecting..."
        )

        self.sws.connect()

    # =====================================================
    # CALLBACK REGISTRATION
    # =====================================================

    def _setup_callbacks(self):

        self.sws.on_open = self.on_open
        self.sws.on_data = self.on_data
        self.sws.on_error = self.on_error
        self.sws.on_close = self.on_close

    # =====================================================
    # ON OPEN
    # =====================================================

    def on_open(self, wsapp):

        logger.info(
            "[SPOT WS] Connected"
        )
        

        self.connected = True

        self.sws.subscribe(
            self.correlation_id,
            self.mode,
            self.token_list
        )

    # =====================================================
    # ON DATA
    # =====================================================

    def on_data(
        self,
        wsapp,
        message
    ):

        if "last_traded_price" not in message:
            return

        tick = {

            "price":
                message["last_traded_price"] / 100,


            "timestamp":
                message["exchange_timestamp"]

        }

        #print(tick)
        self.tick_handler.handle_tick(tick)

    # =====================================================
    # ON ERROR
    # =====================================================

    def on_error(
        self,
        wsapp,
        error
    ):

        logger.error(
            f"[SPOT WS] {error}"
        )

    # =====================================================
    # ON CLOSE
    # =====================================================

    def on_close(
        self,
        wsapp
    ):

        self.connected = False

        logger.info(
            "[SPOT WS] Closed"
        )

    # =====================================================
    # STOP CONNECTION
    # =====================================================

    def stop(self):

        if self.sws:

            print(
                "[SPOT WS] Closing..."
            )

            self.sws.close_connection()





# ws = SpotWebSocket(auth)
# ws.connect()
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from logzero import logger

from .token_resolver import token_resolver
import traceback

class OptionWebsocket:


    def __init__(self, session):

        """Initialize the WebSocket handler with auth and tick handler objects."""
        self.connected = False
        self.session = session
        self.sws = None
        self.correlation_id = "option_ws"
        self.engine = None
        self.current_symbol = None
        self.current_token = None
        self.mode = 1  # Quote mode
        

    def _setup_callbacks(self):
        """Assign WebSocket callbacks."""
        self.sws.on_open = self.on_open
        self.sws.on_data = self.on_data
        self.sws.on_error = self.on_error
        self.sws.on_close = self.on_close

    def on_data(self, wsapp, message):

        try:

            if "last_traded_price" not in message:
                return

            if self.engine is None:
                return

            self.engine.on_option_tick(
                price=message["last_traded_price"] / 100,
                ts=message["exchange_timestamp"]
            )

        except Exception:
            traceback.print_exc()
            raise

        
       
        

    def on_open(self, wsapp):
        """Handle WebSocket open event."""
        
        self.connected = True
        print("[OPION WS] connection successfully.")
        
        #self.sws.subscribe(self.correlation_id, self.mode, self.token_list)


    def subscribe(self, symbol, engine):

        if not self.connected:
            print("[OPTION WS] Not connected")
            return

        self.current_symbol = symbol
        self.engine = engine

        try:
            # Resolve token
            token = token_resolver.get_token(symbol)

            if token is None:
                raise ValueError(f"No token found for symbol: {symbol}")

            self.current_token = token

            token_list = [
                {
                    "exchangeType": 2,
                    "tokens": [str(token)]   # SmartAPI expects string tokens
                }
            ]

            print("\n========== STAGE 3 ==========")
            print("[STAGE 3] Subscribing")
            print(f"Symbol      : {symbol}")
            print(f"Token       : {token}")
            print(f"Payload     : {token_list}")
            print(f"Connected   : {self.connected}")
            print(f"Correlation : {self.correlation_id}")
            print(f"Mode        : {self.mode}")

            self.sws.subscribe(
                self.correlation_id,
                self.mode,
                token_list
            )

            print("[OPTION WS] Subscription request sent successfully.")
            print("=============================\n")

        except Exception as e:
            print("\n========== SUBSCRIBE ERROR ==========")
            print(f"Symbol : {symbol}")
            print(f"Error  : {e}")
            traceback.print_exc()
            print("=====================================\n")
            raise


    def unsubscribe(self):

        if self.current_token is None:
            return

        token_list = [
            {
                "exchangeType": 2,
                "tokens": [self.current_token]
            }
        ]

        self.sws.unsubscribe(
            self.correlation_id,
            self.mode,
            token_list
        )

        print(f"[OPTION WS] Unsubscribed -> {self.current_symbol}")

        self.current_symbol = None
        self.current_token = None
        self.engine = None


    def on_error(self, wsapp, error):
        """Handle WebSocket errors."""
        logger.error(f"WebSocket error: {error}")

    def on_close(self, wsapp):
        """Handle WebSocket close event."""
        logger.info("[OPION WS] disconnect successfully.")
        self.connected = False

    def close_connection(self):
        """Manually close the WebSocket connection."""
        if self.sws:
            self.sws.close_connection()

    def connect(self):

        """Initialize and start the WebSocket connection."""
        AUTH_TOKEN = self.session["auth_token"]
        API_KEY = self.session["api_key"]
        CLIENT_CODE = self.session["client_id"]
        FEED_TOKEN = self.session["feed_token"]

        # Initialize SmartWebSocketV2
        self.sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)
        
        # Setup callbacks
        self._setup_callbacks()

        print("Connecting to WebSocket...")
        
        
        # Start connection
        self.sws.connect()









from fyers_apiv3.FyersWebsocket.tbt_ws import FyersTbtSocket, SubscriptionModes
from utils.time_utils import is_market_open
import time


class OptionWebSocket:

    def __init__(self, access_token):
        self.active = True
        self.current_symbol = None
        self.engine = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        self.reconnect_cooldown = 10

        self.fyers = FyersTbtSocket(
            access_token=access_token,
            write_to_file=False,
            log_path="",
            on_open=self.onopen,
            on_close=self.onclose,
            on_error=self.onerror,
            on_depth_update=self.on_depth_update,
            on_error_message=self.onerror_message
        )

    # Connect once at system start
    def connect(self):
        print("[WS] Starting persistent option socket...")
        self.fyers.connect()

    # Subscribe dynamically when trade starts
    def subscribe(self, symbol, engine):
        print(f"[WS] Subscribing to {symbol}")

        self.current_symbol = symbol
        self.engine = engine

        self.fyers.subscribe(
            symbol_tickers=[symbol],
            channelNo='1',
            mode=SubscriptionModes.DEPTH
        )

    # Unsubscribe on trade exit
    def unsubscribe(self):
        if not self.current_symbol:
            return

        print(f"[WS] Unsubscribing {self.current_symbol}")

        try:
            self.fyers.unsubscribe(
                symbol_tickers=[self.current_symbol],
                channelNo='1'
            )
        except:
            pass

        self.current_symbol = None
        self.engine = None

    def onopen(self):
        print("[WS] Connected.")
        self.reconnect_attempts = 0
        self.fyers.keep_running()

    def on_depth_update(self, ticker, message):
        if not self.engine:
            return

        ltp = (message.bidprice[0] + message.askprice[0]) / 2
        bid = message.bidprice[0]
        ask = message.askprice[0]
        ts = message.timestamp

        self.engine.on_option_tick(ltp, bid, ask, ts)

    def onerror(self, msg):
        print("WS Error:", msg)

        if not self.active:
            return

        now = int(time.time())

        if not is_market_open(now):
            print("[WS] Market closed. Stopping reconnect.")
            self.active = False
            return

        # Stop completely on rate limit
        if "429" in str(msg):
            print("[WS] Rate limited. Stopping reconnect.")
            self.active = False
            return

        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            print(f"[WS] Reconnecting ({self.reconnect_attempts})...")
            time.sleep(self.reconnect_cooldown)
            self.connect()
        else:
            print("[WS] Max reconnect attempts reached.")
            self.active = False

    def onclose(self, msg):
        print("WS Closed:", msg)

    def onerror_message(self, msg):
        print("WS Server Error:", msg)
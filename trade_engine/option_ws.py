from fyers_apiv3.FyersWebsocket.tbt_ws import FyersTbtSocket, SubscriptionModes
from utils.time_utils import is_market_open
import time

class OptionWebSocket:

    def __init__(self, access_token, engine, symbol):
        self.engine = engine
        self.symbol = symbol
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        self.reconnect_cooldown = 15   # seconds
        self.active = True

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

 

    def onerror(self, msg):
        print("WS Error:", msg)

        if not self.active:
            return

        now = int(time.time())

        # 🔒 Market closed → Stop permanently
        if not is_market_open(now):
            print("[WS] Market closed. Stopping reconnect.")
            self.active = False
            return

        # 🚫 Rate limited (429)
        if "429" in str(msg):
            print("[WS] Rate limited. Cooling down...")
            time.sleep(60)
            return

        # 🔁 Controlled reconnect
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            print(f"[WS] Reconnecting ({self.reconnect_attempts}/{self.max_reconnect_attempts})...")
            time.sleep(self.reconnect_cooldown)
            self.connect()
        else:
            print("[WS] Max reconnect attempts reached. Giving up.")
            self.active = False


    def onopen(self):

        # ✅ RESET reconnect attempts when connection succeeds
        self.reconnect_attempts = 0
        mode = SubscriptionModes.DEPTH
        channel = '1'

        self.fyers.subscribe(
            symbol_tickers=[self.symbol],
            channelNo=channel,
            mode=mode
        )

        self.fyers.switchChannel(
            resume_channels=[channel],
            pause_channels=[]
        )

        self.fyers.keep_running()

    # 🔥 IMPORTANT PART
    def on_depth_update(self, ticker, message):

        ltp_price = (message.bidprice[0] + message.askprice[0]) / 2
        bid = message.bidprice[0]
        ask = message.askprice[0]
        ts = message.timestamp

        self.engine.on_option_tick(ltp_price, bid, ask, ts)

    def onerror(self, msg):
        print("WS Error:", msg)

        now = int(time.time())

        # 1️⃣ If market closed → STOP
        if not is_market_open(now):
            print("[WS] Market closed. Not reconnecting.")
            return

        # 2️⃣ If rate limited (429) → cooldown
        if "429" in str(msg):
            print("[WS] Rate limited. Cooling down 60 seconds...")
            time.sleep(60)
            return

    def onclose(self, msg):
        print("WS Closed:", msg)

    def onerror_message(self, msg):
        print("WS Server Error:", msg)

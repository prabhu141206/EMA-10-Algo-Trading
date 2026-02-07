from fyers_apiv3.FyersWebsocket.tbt_ws import FyersTbtSocket, SubscriptionModes

class OptionWebSocket:

    def __init__(self, access_token, engine, symbol):
        self.engine = engine
        self.symbol = symbol

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

    def connect(self):
        self.fyers.connect()

    def onopen(self):
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

        price = (message.bidprice[0] + message.askprice[0]) / 2
        bid = message.bidprice[0]
        ask = message.askprice[0]
        ts = message.timestamp

        self.engine.on_option_tick(price, bid, ask, ts)

    def onerror(self, msg):
        print("WS Error:", msg)

    def onclose(self, msg):
        print("WS Closed:", msg)

    def onerror_message(self, msg):
        print("WS Server Error:", msg)
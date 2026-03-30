from fyers_apiv3.FyersWebsocket import data_ws
from config.settings import CLIENT_ID, ACCESS_TOKEN
import warnings
warnings.filterwarnings("ignore")


def start(tick_handler):

    ws_token = f"{CLIENT_ID}:{ACCESS_TOKEN}"

    # ----- CALLBACKS -----

    def onmessage(message):

        if "ltp" not in message:
            return

        tick = {
            "price": message["ltp"],
            "timestamp": message["exch_feed_time"],
            "symbol": message["symbol"]
        }

        #Testing tick (1)
        #print(f"[TICK] {tick['symbol']} @ {tick['price']}")

        tick_handler.handle_tick(tick)

    def onerror(message):
        print("Index WS Error:", message)

    def onclose(message):
        print("Index WS Closed:", message)

    def onopen():
        data_type = "SymbolUpdate"
        symbols = ["NSE:NIFTY50-INDEX"]

        fyers.subscribe(symbols=symbols, data_type=data_type)
        fyers.keep_running()

    # ----- CREATE SOCKET -----

    fyers = data_ws.FyersDataSocket(
        access_token=ws_token,
        log_path="",
        litemode=False,
        write_to_file=False,
        reconnect=True,
        on_connect=onopen,
        on_close=onclose,
        on_error=onerror,
        on_message=onmessage
    )

    fyers.connect()
from fyers_apiv3.FyersWebsocket import data_ws
from core.tick_handler import tick_handler
import warnings
warnings.filterwarnings("ignore")

# ----- CALLBACKS -----
def onmessage(message):
    if "ltp" not in message:
        return

    tick = {
        "price": message["ltp"],
        "timestamp": message["exch_feed_time"],
        "symbol": message["symbol"]
    }
    tick_handler.handle_tick(tick)


def onerror(message):
    print("Error:", message)


def onclose(message):
    print("Connection closed:", message)


def onopen():
    data_type = "SymbolUpdate"
    symbols = ["NSE:NIFTY50-INDEX"]

    fyers.subscribe(symbols=symbols, data_type=data_type)
    fyers.keep_running()


# ----- AUTH -----
client_id = "RFX****G77-100"
access_token = "eweqwvffsf*******qeqadsd"

ws_token = f"{client_id}:{access_token}"

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

# ----- CONNECT -----
def start():
    fyers.connect()

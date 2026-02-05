from fyers_apiv3.FyersWebsocket import data_ws
from core.tick_handler import tick_handler
from dotenv import load_dotenv
import os
import warnings

warnings.filterwarnings("ignore")

# ================= LOAD ENV =================
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

if not CLIENT_ID or not ACCESS_TOKEN:
    raise Exception("❌ CLIENT_ID or ACCESS_TOKEN missing from environment")

WS_TOKEN = f"{CLIENT_ID}:{ACCESS_TOKEN}"

# ================= CALLBACKS =================

def onmessage(message):

    if "ltp" not in message:
        return

    if "exch_feed_time" not in message:
        return

    if not message["exch_feed_time"]:
        return

    ts = int(message["exch_feed_time"] / 1000)

    # Reject invalid timestamps
    if ts < 1600000000:   # anything before 2020 → junk
        return

    tick = {
        "price": message["ltp"],
        "timestamp": ts,
        "symbol": message["symbol"]
    }

    tick_handler.handle_tick(tick)

def onerror(message):
    print("❌ Socket Error:", message)


def onclose(message):
    print("🔴 Connection Closed:", message)


def onopen():
    """
    Runs when websocket connects
    """

    print("✅ FYERS Websocket Connected")

    symbols = ["NSE:NIFTY50-INDEX"]
    data_type = "SymbolUpdate"

    fyers.subscribe(symbols=symbols, data_type=data_type)
    fyers.keep_running()

    print("📡 Subscribed to:", symbols)


# ================= CREATE SOCKET =================

fyers = data_ws.FyersDataSocket(
    access_token=WS_TOKEN,
    log_path="",
    litemode=False,
    write_to_file=False,
    reconnect=True,
    on_connect=onopen,
    on_close=onclose,
    on_error=onerror,
    on_message=onmessage
)


# ================= START SOCKET =================

def start():
    print("===================================")
    print("🚀 Starting EMA Trend Algo")
    print("🔐 CLIENT ID:", CLIENT_ID)
    print("🔑 TOKEN LENGTH:", len(ACCESS_TOKEN))
    print("===================================")

    fyers.connect()
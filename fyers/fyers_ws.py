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
    """
    Called whenever new tick arrives
    """

    # Ignore packets without price
    if "ltp" not in message:
        return

    exch_time = message.get("exch_feed_time")

    # ----- SAFETY CHECK -----
    if not exch_time or exch_time <= 0:
        return

    # Convert milliseconds → seconds
    timestamp = int(exch_time / 1000)

    tick = {
        "price": message["ltp"],
        "timestamp": timestamp,
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
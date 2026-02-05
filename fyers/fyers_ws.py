from fyers_apiv3.FyersWebsocket import data_ws
from core.tick_handler import tick_handler
from dotenv import load_dotenv
import os
import warnings

warnings.filterwarnings("ignore")
load_dotenv()


# ================= CALLBACKS =================

def onmessage(message):
    print("📡 RAW MESSAGE RECEIVED:", message)

    if "ltp" not in message:
        return

    tick = {
        "price": message["ltp"],
        "timestamp": message["exch_feed_time"],
        "symbol": message["symbol"]
    }

    print("✅ TICK FORWARDED TO HANDLER")
    tick_handler.handle_tick(tick)


def onerror(message):
    print("❌ FYERS ERROR:", message)


def onclose(message):
    print("⚠️ CONNECTION CLOSED:", message)


def onopen():
    print("🟢 WEBSOCKET CONNECTED SUCCESSFULLY")

    data_type = "SymbolUpdate"
    symbols = ["NSE:NIFTY50-INDEX"]

    print("📊 Subscribing to symbols:", symbols)

    fyers.subscribe(symbols=symbols, data_type=data_type)
    fyers.keep_running()


# ================= AUTH =================

client_id = os.getenv("CLIENT_ID")
access_token = os.getenv("ACCESS_TOKEN")

print("===== DEBUG AUTH =====")
print("CLIENT ID:", client_id)
print("ACCESS TOKEN LENGTH:", len(access_token) if access_token else None)
print("======================")

ws_token = f"{client_id}:{access_token}"


# ================= SOCKET =================

print("🛠 Creating Fyers Websocket...")

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


# ================= CONNECT =================

def start():
    print("🚀 Connecting to FYERS Websocket...")
    fyers.connect()
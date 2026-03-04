
# Fyers WS for index import
from fyers.fyers_ws import start as start_index_ws

# Telegram imports 
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import system_start


# DB imports
from db.worker import start_db_worker
from db.init_tables import init_tables
from utils.time_utils import wait_until_market_open
import threading

from trade_engine.option_ws import OptionWebSocket
from trade_engine.virtual_trade_engine import VirtualTradeEngine
from core.breakout_watcher import BreakoutWatcher
from core.tick_handler import TickHandler

from config.settings import ACCESS_TOKEN


def main():

    # -------------------------------------------------
    # 1️⃣ Initialize DB
    # -------------------------------------------------
    init_tables()

    print("Starting EMA Trend Algo...")
    print("Waiting for ticks from FYERS...\n")

    telegram_alert.send(system_start())

    # -------------------------------------------------
    # 2️⃣ Start DB Worker (Background Thread)
    # -------------------------------------------------
    threading.Thread(
        target=start_db_worker,
        daemon=True
    ).start()

    # -------------------------------------------------
    # 3️⃣ Create Persistent Option WebSocket
    # -------------------------------------------------
    option_ws = OptionWebSocket(
        access_token=ACCESS_TOKEN
    )

    # Connect once for whole session
    option_ws.connect()

    # -------------------------------------------------
    # 4️⃣ Create Trading Engine (Inject Option WS)
    # -------------------------------------------------
    engine = VirtualTradeEngine(option_ws)

    # -------------------------------------------------
    # 5️⃣ Create BreakoutWatcher (Inject Engine)
    # -------------------------------------------------
    breakout_watcher = BreakoutWatcher(engine)

    # -------------------------------------------------
    # 6️⃣ Create TickHandler (Inject BreakoutWatcher)
    # -------------------------------------------------
    tick_handler = TickHandler(breakout_watcher)

    # -------------------------------------------------
    # 7️⃣ Wait Until Market Open
    # -------------------------------------------------
    wait_until_market_open()

    # -------------------------------------------------
    # 8️⃣ Start Index WebSocket (Inject TickHandler)
    # -------------------------------------------------
    start_index_ws(tick_handler)


if __name__ == "__main__":
    main()
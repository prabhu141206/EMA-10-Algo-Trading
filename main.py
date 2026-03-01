from fyers.fyers_ws import start as start_index_ws
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import system_start
import threading
from db.worker import start_db_worker
from db.init_tables import init_tables
from utils.time_utils import wait_until_market_open
from trade_engine.option_ws import OptionWebSocket
from trade_engine.virtual_trade_engine import VirtualTradeEngine
from config.settings import ACCESS_TOKEN


def main():

    init_tables()

    print("Starting EMA Trend Algo...")
    print("Waiting for ticks from FYERS...\n")

    telegram_alert.send(system_start())

    # Start DB worker
    threading.Thread(target=start_db_worker, daemon=True).start()

    # Wait for market open
    wait_until_market_open()

    # -------------------------------------------------
    # 1️⃣ Start persistent OPTION WebSocket
    # -------------------------------------------------
    option_ws = OptionWebSocket(ACCESS_TOKEN)
    option_ws.connect()

    # -------------------------------------------------
    # 2️⃣ Create Engine and inject websocket
    # -------------------------------------------------
    engine = VirtualTradeEngine(option_ws)

    # IMPORTANT:
    # If breakout_watcher currently creates its own engine,
    # you must modify it to accept this engine instance.
    # (Dependency injection — production pattern)

    # -------------------------------------------------
    # 3️⃣ Start INDEX WebSocket
    # -------------------------------------------------
    start_index_ws()


if __name__ == "__main__":
    main()
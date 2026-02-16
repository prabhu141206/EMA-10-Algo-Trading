"""
ENTRY POINT OF THE PROGRAM
"""

# IMPORTANT:
# Import core modules FIRST so objects are created once
from core.tick_handler import tick_handler  # noqa: F401
from core.candle_builder import candle_builder  # noqa: F401
from core.signal_engine import signal_engine  # noqa: F401
from core.state_machine import state_machine  # noqa: F401
from core.breakout_watcher import breakout_watcher  # noqa: F401
from config import settings
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
from fyers.fyers_ws import start
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import system_start
import threading
from db.worker import start_db_worker
from db.init_tables import init_tables
from utils.time_utils import wait_until_market_open

    


def main():
    init_tables()
    print("Starting EMA Trend Algo...")
    print("Waiting for ticks from FYERS...\n")

    # ⭐ SEND TELEGRAM ALERT HERE
    telegram_alert.send(system_start())

    # DB connection is started
    threading.Thread(target=start_db_worker, daemon=True).start()

    wait_until_market_open()
    # Start FYERS WebSocket
    start()



if __name__ == "__main__":
    main()

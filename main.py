# =========================================================
# INDEX WEBSOCKET ENTRYPOINT
# This starts the live market data stream for the index.
# All index ticks will eventually flow into TickHandler.
# =========================================================
from fyers.fyers_ws import start as start_index_ws


# =========================================================
# TELEGRAM ALERT SYSTEM
# Used only for observability (system notifications).
# Does NOT affect trading logic.
# =========================================================
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import system_start


# =========================================================
# THREADING
# Used to run DB worker asynchronously so trading logic
# never blocks on database writes.
# =========================================================
import threading


# =========================================================
# DATABASE LAYER
# init_tables() → ensures DB schema exists
# start_db_worker() → background thread that writes logs
# =========================================================
from db.worker import start_db_worker
from db.init_tables import init_tables


# =========================================================
# TIME CONTROL UTILITIES
# Prevents system from starting trading before market open.
# =========================================================
from utils.time_utils import wait_until_market_open


# =========================================================
# TRADING ENGINE COMPONENTS
# OptionWebSocket → persistent socket for option ticks
# VirtualTradeEngine → manages trade lifecycle
# BreakoutWatcher → detects breakout and triggers entry
# TickHandler → routes index ticks through strategy logic
# =========================================================
from trade_engine.option_ws import OptionWebSocket
from trade_engine.virtual_trade_engine import VirtualTradeEngine
from core.breakout_watcher import BreakoutWatcher
from core.tick_handler import TickHandler


# =========================================================
# CONFIGURATION
# Contains API credentials and environment variables.
# =========================================================
from config.settings import ACCESS_TOKEN



def main():

    # =====================================================
    # 1️⃣ DATABASE INITIALIZATION
    # Ensures required tables exist before system starts.
    # =====================================================
    init_tables()

    print("Starting EMA Trend Algo...")
    print("Waiting for ticks from FYERS...\n")


    # =====================================================
    # 2️⃣ SYSTEM START NOTIFICATION
    # Sends Telegram alert indicating bot has started.
    # Purely informational.
    # =====================================================
    telegram_alert.send(system_start())


    # =====================================================
    # 3️⃣ START DATABASE WORKER THREAD
    # DB writes are handled asynchronously using a queue.
    # This prevents blocking during trade execution.
    # =====================================================
    threading.Thread(
        target=start_db_worker,
        daemon=True
    ).start()


    # =====================================================
    # 4️⃣ CREATE PERSISTENT OPTION WEBSOCKET
    # This socket stays connected throughout the system
    # lifetime and dynamically subscribes to option symbols
    # whenever a trade is triggered.
    # =====================================================
    option_ws = OptionWebSocket(ACCESS_TOKEN)


    # =====================================================
    # 5️⃣ CONNECT OPTION WEBSOCKET
    # Establishes connection to FYERS before trading begins.
    # No symbols are subscribed yet.
    # =====================================================
    option_ws.connect()


    # =====================================================
    # 6️⃣ CREATE TRADING ENGINE
    # Engine owns the trade lifecycle:
    # entry → monitoring → exit → reset
    # Option websocket is injected into engine.
    # =====================================================
    engine = VirtualTradeEngine(option_ws)


    # =====================================================
    # 7️⃣ CREATE BREAKOUT WATCHER
    # Monitors index ticks and triggers entry when breakout
    # condition is satisfied.
    # Delegates trade execution to engine.
    # =====================================================
    breakout_watcher = BreakoutWatcher(engine)


    # =====================================================
    # 8️⃣ CREATE TICK HANDLER
    # First processing layer for index ticks.
    # Responsible for:
    # candle building
    # signal evaluation
    # breakout detection
    # =====================================================
    tick_handler = TickHandler(breakout_watcher)


    # =====================================================
    # 9️⃣ WAIT UNTIL MARKET OPEN
    # Prevents processing of ticks before trading hours.
    # =====================================================
    wait_until_market_open()


    # =====================================================
    # 🔟 START INDEX WEBSOCKET
    # Once started, index ticks will continuously flow
    # through TickHandler → Strategy → Engine.
    # =====================================================
    start_index_ws(tick_handler)



# =========================================================
# PROGRAM ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    main()
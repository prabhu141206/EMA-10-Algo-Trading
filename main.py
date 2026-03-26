# =========================================================
# MAIN ENTRYPOINT FOR TRADING SYSTEM
# =========================================================

# =========================================================
# INDEX WEBSOCKET
# Starts live index tick stream
# =========================================================
from fyers.fyers_ws import start as start_index_ws


# =========================================================
# TELEGRAM ALERT SYSTEM (OBSERVABILITY ONLY)
# =========================================================
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import system_start


# =========================================================
# THREADING (FOR NON-BLOCKING DB WRITES)
# =========================================================
import threading


# =========================================================
# DATABASE LAYER
# =========================================================
from db.worker import start_db_worker
from db.init_tables import init_tables


# =========================================================
# TIME CONTROL (WAIT UNTIL MARKET OPEN)
# =========================================================
from utils.time_utils import wait_until_market_open


# =========================================================
# TRADING COMPONENTS
# =========================================================
from trade_engine.option_ws import OptionWebSocket
from strategy.strategy_manager import StrategyManager
from core.tick_handler import TickHandler


# =========================================================
# CONFIGURATION
# =========================================================
from config.settings import ACCESS_TOKEN


def main():

    # =====================================================
    # 1️⃣ INITIALIZE DATABASE
    # Ensures all required tables exist before system starts
    # =====================================================
    init_tables()

    print("Starting EMA Trend Algo...")
    print("Waiting for ticks from FYERS...\n")


    # =====================================================
    # 2️⃣ SEND SYSTEM START ALERT
    # Purely informational (does NOT affect trading)
    # =====================================================
    telegram_alert.send(system_start())


    # =====================================================
    # 3️⃣ START DATABASE WORKER THREAD
    # Runs in background to avoid blocking trading logic
    # =====================================================
    threading.Thread(
        target=start_db_worker,
        daemon=True
    ).start()


    # =====================================================
    # 4️⃣ CREATE OPTION WEBSOCKET (PERSISTENT)
    # This socket will be reused by all strategies
    # =====================================================
    option_ws = OptionWebSocket(ACCESS_TOKEN)


    # =====================================================
    # 5️⃣ CONNECT OPTION WEBSOCKET
    # Must be connected BEFORE any trade starts
    # =====================================================
    option_ws.connect()


    # =====================================================
    # 6️⃣ CREATE STRATEGY MANAGER
    # Responsible for managing ALL strategies
    # =====================================================
    strategy_manager = StrategyManager(option_ws)


    # =====================================================
    # 7️⃣ REGISTER STRATEGIES
    # Add all index symbols you want to trade
    # =====================================================
    strategy_manager.add_strategy("NSE:NIFTY50-INDEX")
    # strategy_manager.add_strategy("BANKNIFTY")  # future scaling


    # =====================================================
    # 8️⃣ CREATE TICK HANDLER (ROUTER ONLY)
    # This will route incoming ticks to correct strategy
    # =====================================================
    tick_handler = TickHandler(strategy_manager)


    # =====================================================
    # 9️⃣ WAIT UNTIL MARKET OPEN
    # Prevents pre-market noise from corrupting system
    # =====================================================
    wait_until_market_open()


    # =====================================================
    # 🔟 START INDEX WEBSOCKET
    # This is the main event loop (blocking call)
    # Every tick flows into TickHandler
    # =====================================================
    start_index_ws(tick_handler)


# =========================================================
# PROGRAM ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    main()
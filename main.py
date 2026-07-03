# =========================================================
# MAIN ENTRYPOINT FOR TRADING SYSTEM
# =========================================================

# =========================================================
# INDEX WEBSOCKET
# Starts live index tick stream
# =========================================================
import time

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
from utils.Market_calender import market_status


# =========================================================
# TRADING COMPONENTS
# =========================================================
from trade_engine.option_ws import OptionWebSocket
from core.tick_handler import TickHandler


# =========================================================
# CONFIGURATION
# =========================================================
from config.settings import ACCESS_TOKEN


def main():


    # =====================================================
    # 0 CHECK MARKET STATUS
    # Waits until market is open before starting trading logic
    # Prevents Unnecessary system running during market closed hours
    # =====================================================

    market_live = market_status.is_market_live()

    if not market_live: 
        print("\n🔔 Market Status: 🔴 CLOSED.\nWaiting for market to open...\n")

        # Get current time, next trading session time, and seconds until market opens
        current_time, next_open_time, seconds_to_open = market_status.get_next_trading_session_info()
        print(f"🕒 Current Time: {current_time}")
        print(f"⏳ Next Trading Session: {next_open_time}")
        print(f"⏰ Market opens: {seconds_to_open} seconds\n")

        time.sleep(int(seconds_to_open))  # Sleep for the remaining seconds until market opens

    # Market is now open, proceed with the rest of the trading logic and run the system
    print("\n 🔔 Market Status: 🟢 OPEN.\nStarting trading system...\n")

        

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



    tick_handler = TickHandler(option_ws)
    


   


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
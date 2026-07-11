# =========================================================
# MAIN ENTRYPOINT
# =========================================================
#
# Responsibility:
# - Wait until market opens
# - Initialize infrastructure
# - Start database worker
# - Connect broker websockets
# - Start trading event loop
#
# Flow
#
# Market Check
#      ↓
# Database
#      ↓
# Telegram
#      ↓
# DB Worker
#      ↓
# Option WebSocket
#      ↓
# Tick Handler
#      ↓
# Spot WebSocket
#
# =========================================================

import time
import threading

# =========================================================
# BROKER
# =========================================================

from broker_websocket.auth import auth
from broker_websocket.OptionwebSocket import OptionWebsocket
from broker_websocket.SpotwebSocket import SpotWebSocket

# =========================================================
# TRADING ENGINE
# =========================================================

from core.tick_handler import TickHandler

# =========================================================
# DATABASE
# =========================================================

from db.init_tables import init_tables
from db.worker import start_db_worker

# =========================================================
# ALERTS
# =========================================================

from alerts.telegram_alert import telegram_alert
from alerts.message_templates import system_start

# =========================================================
# MARKET CALENDAR
# =========================================================

from utils.Market_calender import market_status


def main():

    # =====================================================
    # 1️⃣ WAIT FOR MARKET OPEN
    # =====================================================

    if not market_status.is_market_live():
    
        print(
            "\n🔔 Market Closed.\n"
            "Waiting for next trading session...\n"
        )
    
        current, next_open, seconds = (
            market_status.get_next_trading_session_info()
        )
    
        print(f"Current Time : {current}")
        print(f"Next Session : {next_open}")
        print(f"Waiting      : {seconds} sec\n")
    
        time.sleep(int(seconds))
    
    print(
        "\n🔔 Market Open."
        "\nStarting Trading System...\n"
    )

    # =====================================================
    # 2️⃣ INITIALIZE DATABASE
    # =====================================================

    init_tables()

    print("Starting EMA Trend Algo...")
    print("Waiting for SmartAPI ticks...\n")

    # =====================================================
    # 3️⃣ SEND STARTUP ALERT
    # =====================================================

    telegram_alert.send(
        system_start()
    )

    # =====================================================
    # 4️⃣ START DATABASE WORKER
    # =====================================================

    db_worker = threading.Thread(
        target=start_db_worker,
        daemon=True
    )

    db_worker.start()

    # =====================================================
    # 5️⃣ CREATE OPTION WEBSOCKET
    # =====================================================

    option_ws = OptionWebsocket(auth)

    # =====================================================
    # 6️⃣ START OPTION WEBSOCKET
    # =====================================================

    option_ws_thread = threading.Thread(
        target=option_ws.connect,
        daemon=True
    )

    option_ws_thread.start()

    # =====================================================
    # 7️⃣ CREATE TICK HANDLER
    # =====================================================

    tick_handler = TickHandler(
        option_ws
    )

    # =====================================================
    # 8️⃣ CREATE SPOT WEBSOCKET
    # =====================================================

    spot_ws = SpotWebSocket(
        auth,
        tick_handler
    )

    # =====================================================
    # 9️⃣ START SPOT WEBSOCKET
    # =====================================================

    spot_ws_thread = threading.Thread(
        target=spot_ws.connect,
        daemon=True
    )

    spot_ws_thread.start()

    # =====================================================
    # 🔟 KEEP MAIN THREAD ALIVE
    # =====================================================

    option_ws_thread.join()
    spot_ws_thread.join()


# =========================================================
# PROGRAM ENTRYPOINT
# =========================================================

if __name__ == "__main__":
    main()
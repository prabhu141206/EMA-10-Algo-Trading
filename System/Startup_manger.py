# =========================================================
# STARTUP MANAGER
# =========================================================
#
# Responsibility
# - Initialize trading infrastructure
# - Wire system dependencies
# - Start trading system
#
# =========================================================

# =========================================================
# ALERTS
# =========================================================
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import system_start


# =========================================================
# TRADING ENGINE
# =========================================================
from core.tick_handler import TickHandler


# =========================================================
# BROKER
# =========================================================
from broker_websocket.OptionwebSocket import OptionWebsocket
from broker_websocket.SpotwebSocket import SpotWebSocket
from broker_websocket.auth.auth import auth


# =========================================================
# DATABASE
# =========================================================
import threading
from db.init_tables import init_tables
from db.worker import start_db_worker


class StartupManager:

    def __init__(self):

        self.session = None
        self.db_worker = None
        self.option_ws = None
        self.option_ws_thread = None
        self.tick_handler = None
        self.spot_ws = None
        self.spot_ws_thread = None


    # =====================================================
    # INITIALIZE AUTHENTICATION
    # =====================================================

    def _initialize_auth(self):

        print("[STARTUP] Initializing authentication...")

        self.session = auth.get_session()

        print("[STARTUP] Authentication ready.")


    # =====================================================
    # INITIALIZE OPTION WEBSOCKET
    # =====================================================

    def _initialize_option_websocket(self):

        print("[STARTUP] Initializing Option WebSocket...")

        self.option_ws = OptionWebsocket(
            session=self.session
        )

        self.option_ws_thread = threading.Thread(
            target=self.option_ws.connect,
            daemon=True
        )

        self.option_ws_thread.start()

        print("[STARTUP] Option WebSocket Started.")


    # =====================================================
    # INITIALIZE SPOT WEBSOCKET
    # =====================================================

    def _initialize_spot_websocket(self):

        
        # =====================================================
        # CREATE TICK HANDLER
        # =====================================================

        self.tick_handler = TickHandler(
            self.option_ws
        )

        # =====================================================
        # CREATE SPOT WEBSOCKET
        # =====================================================

        print("[STARTUP] Initializing Spot WebSocket...")

        self.spot_ws = SpotWebSocket(
            session = self.session,
            tick_handler = self.tick_handler
        )
            
        # =====================================================
        # START SPOT WEBSOCKET
        # =====================================================

        self.spot_ws_thread = threading.Thread(
            target=self.spot_ws.connect,
            daemon=True
        )

        self.spot_ws_thread.start()


    # =====================================================
    # INITIALIZE DB AND WORKER
    # =====================================================
    def _initialize_db(self):

        # =====================================================
        # START DATABASE WORKER AND INITIALIZE TABLE
        # =====================================================
        init_tables()
        self.db_worker = threading.Thread(
            target=start_db_worker,
            daemon=True
        )

        self.db_worker.start()


    # =====================================================
    # SEND STARTUP ALERT
    # =====================================================

    def _initial_msg(self):
        telegram_alert.send(
            system_start()
        )
    
    # =====================================================
    # KEEPING APPLICATION RUNNING
    # =====================================================

    def run(self):
        self.option_ws_thread.join()
        self.spot_ws_thread.join()

    def start(self):

        # =====================================================
        # INITIALIZE ALL STARTUP THINGS
        # =====================================================
        self._initialize_db()
        self._initialize_auth()
        self._initialize_option_websocket()
        self._initialize_spot_websocket()
        self._initial_msg()
        
        
      
        print("Starting EMA Trend Algo...")
        print("Waiting for SmartAPI ticks...\n")


        


    

        
            



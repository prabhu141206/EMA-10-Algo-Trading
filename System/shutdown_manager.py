# =========================================================
# SHUTDOWN MANAGER
# =========================================================
#
# Responsibility:
# - Gracefully stop the trading system
# - Release all resources
# - Prepare application for next startup
#
# =========================================================

from datetime import datetime, time 
from db.worker import stop_db_worker
from db.queue import db_queue
from db.pool import close_pool

class ShutdownManager:

    def __init__(self):

        # Broker Components
        self.spot_ws = None
        self.option_ws = None

        # Thread References
        self.spot_ws_thread = None
        self.option_ws_thread = None

        # Trading Components
        self.state_machine = None
        self.engine = None

        # Database
        self.db_worker_thread = None

        # Authentication
        self.auth = None



    # =====================================================
    # GIVIN ALL ACCESS TO SHUTDOWN MANAGER
    # =====================================================

    def initialize(
        self,
        spot_ws,
        option_ws,
        spot_ws_thread,
        option_ws_thread,
        db_worker_thread,
        state_machine,
        engine,
        auth
    ):

        self.spot_ws = spot_ws
        self.option_ws = option_ws

        self.spot_ws_thread = spot_ws_thread
        self.option_ws_thread = option_ws_thread

        self.db_worker = db_worker_thread

        self.state_machine = state_machine
        self.engine = engine

        self.auth = auth

    # =====================================================
    # FLUSH DATABASE QUEUE
    # =====================================================

    def flush_database_queue(self):

        print("[SHUTDOWN] Waiting for pending database tasks...")

        db_queue.join()

        print("[SHUTDOWN] Database queue flushed.")

    # =====================================================
    # STOP DB WORKER
    # =====================================================

    def stop_db_worker(self):

        print("[SHUTDOWN] Stopping DB Worker...")

        stop_db_worker()

        print("[SHUTDOWN] DB Worker stopped.")


    # =====================================================
    # WAIT FOR DB WORKER
    # =====================================================

    def wait_for_db_worker(self):

        print("[SHUTDOWN] Waiting for DB Worker...")

        if self.db_worker_thread is not None:

            self.db_worker_thread.join()



    print("[SHUTDOWN] DB Worker stopped.")
    # =====================================================
    # WAIT FOR WEBSOCKET THREADS
    # =====================================================

    def wait_for_websocket_threads(self):

        print("[SHUTDOWN] Waiting for WebSocket threads...")

        if self.spot_ws_thread is not None:
            self.spot_ws_thread.join()

        if self.option_ws_thread is not None:
            self.option_ws_thread.join()

        print("[SHUTDOWN] WebSocket threads stopped.")
    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    def close_database(self):

        print("[SHUTDOWN] Closing database...")

        close_pool()

        print("[SHUTDOWN] Database closed.")

    # =====================================================
    # RELEASE RESOURCES
    # =====================================================

    def release_resources(self):

        print("[SHUTDOWN] Releasing system resources...")


    # =====================================================
    # LOGOUT
    # =====================================================

    def logout(self):

        print("[SHUTDOWN] Logging out from SmartAPI...")


    # =====================================================
    # STOP OPTION WEBSOCKET
    # =====================================================

    def stop_option_websocket(self):

        print("[SHUTDOWN] Stopping Option WebSocket...")

        if self.option_ws is not None:

            self.option_ws.stop()

        print("[SHUTDOWN] Option WebSocket stopped.")


    # =====================================================
    # STOP SPOT WEBSOCKET
    # =====================================================

    def stop_spot_websocket(self):

        print("[SHUTDOWN] Stopping Spot WebSocket...")

        if self.spot_ws is not None:

            self.spot_ws.stop()

        print("[SHUTDOWN] Spot WebSocket stopped.")


    # =====================================================
    # SHUTDOWN SYSTEM
    # =====================================================

    def shutdown(self):

        print("\n" + "=" * 60)
        print("[SHUTDOWN] Starting graceful shutdown...")
        print("=" * 60)

        self.stop_spot_websocket()
        self.stop_option_websocket()
        self.wait_for_websocket_threads()
        self.flush_database_queue()
        self.stop_db_worker()
        self.wait_for_db_worker()
        self.close_database()

        print("[SHUTDOWN] Shutdown complete.")



    # =====================================================
    # HANDLE IDLE STATE
    # =====================================================

    def handle_idle_state(self):

        print("[SHUTDOWN] Strategy is idle.")
        print("[SHUTDOWN] Safe to shutdown.")

        self.shutdown()
    

    # =====================================================
    # HANDLE TRIGGER STATE
    # =====================================================

    def handle_trigger_state(self):

        print("[SHUTDOWN] Trigger is armed.")
        print("[SHUTDOWN] Cancelling pending trigger.")

        self.state_machine.expire_trigger()

        self.shutdown()

    # =====================================================
    # HANDLE IN TRADE STATE
    # =====================================================

    def handle_in_trade_state(self):

        print("[SHUTDOWN] Active trade detected.")
        print("[SHUTDOWN] Waiting for trade completion.")





    # =====================================================
    # EVALUATE STRATEGY STATE
    # =====================================================

    def evaluate_strategy_state(self):

        state = self.state_machine.state

        print(f"[SHUTDOWN] Current Strategy State : {state}")

        if state == "IDLE":

            self.handle_idle_state()

        elif state == "TRIGGER_ARMED":

            self.handle_trigger_state()

        elif state == "IN_TRADE":

            self.handle_in_trade_state()

        else:

            print(
                f"[SHUTDOWN] Unknown state : {state}"
            )

    # =====================================================
    # CHECK MARKET CLOSE
    # =====================================================

    def check_market_close(self):

        current_time = datetime.now().time()

        market_close_time = time(15, 0)

        # -----------------------------------------------
        # Market Still Open
        # -----------------------------------------------

        if current_time < market_close_time:
            return

        # -----------------------------------------------
        # Market Close Detected
        # -----------------------------------------------

        print("[SHUTDOWN] Market close detected.")

        self.evaluate_strategy_state()


shutdown_manager = ShutdownManager()


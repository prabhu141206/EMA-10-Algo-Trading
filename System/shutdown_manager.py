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

        # Add shutdowns flag
        self.shutdown_started = False
        self.partial_shutdown_done = False

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

        self.db_worker_thread = db_worker_thread

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

        if self.auth is not None:

            try:
                self.auth.logout()

                print("[SHUTDOWN] SmartAPI logout successful.")

            except Exception as e:

                print(f"[SHUTDOWN] Logout failed: {e}")


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
    # TRADE COMPLETED
    # =====================================================

    def trade_completed(self):

        print("[SHUTDOWN] Active trade completed.")

        self.shutdown()


    # =====================================================
    # SHUTDOWN SYSTEM
    # =====================================================

    def shutdown(self):

        if self.shutdown_started:
            print("[SHUTDOWN] Shutdown already in progress.")
            return

        self.shutdown_started = True

        

        print("\n" + "=" * 60)
        print("[SHUTDOWN] Starting graceful shutdown...")
        print("=" * 60)

        if not self.partial_shutdown_done :
            self.stop_spot_websocket()

            
        self.stop_option_websocket()
        self.wait_for_websocket_threads()
        self.flush_database_queue()
        self.stop_db_worker()
        self.wait_for_db_worker()
        self.close_database()
        self.logout()

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

        print("[SHUTDOWN] Strategy State : IN_TRADE")
        print("[SHUTDOWN] Initiating forced trade exit...")

        self.partial_shutdown()

        


    
    

    # =====================================================
    # PARTIAL SHUTDOWN SYSTEM
    # =====================================================
    def partial_shutdown(self):

        if self.partial_shutdown_done:
            return

        self.partial_shutdown_done = True

        print("[SHUTDOWN] Starting partial shutdown...")

        self.stop_spot_websocket()

        print("[SHUTDOWN] Waiting for active trade to complete...")
    


    # =====================================================
    # IS FORCE EXIT TIME
    # =====================================================

    def is_force_exit_time(self):

        current_time = datetime.now().time()

        force_exit_time = time(15, 25)

        return current_time >= force_exit_time

    def is_time_to_shutdown(self):

        current_time = datetime.now().time()

        return current_time >= time(15, 0)


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


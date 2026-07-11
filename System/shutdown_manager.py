from datetime import datetime
from datetime import time as dt_time


class ShutdownManager:

    def __init__(self):

        self.shutdown_pending = False
        self.shutdown_started = False

    def request_shutdown(self):

        self.shutdown_pending = True

        print(
            "[SHUTDOWN] "
            "Shutdown pending..."
        )

        print(
            "[SHUTDOWN] "
            "Trade active. Waiting for exit."
        )

    def is_shutdown_pending(self):

        return self.shutdown_pending
    
    def shutdown(self):

        if self.shutdown_started:
            return

        self.shutdown_started = True

        print(
            "[SHUTDOWN] "
            "Graceful shutdown started."
        )


    def check_market_close(self,state_machine):

        now = datetime.now().time()

        market_close = dt_time(
            15,
            0
        )

        if now < market_close:
            return

        print(
            "[SHUTDOWN] "
            "Market close detected."
        )


        # =====================================
        # IN TRADE
        # =====================================

        if state_machine.is_in_trade():

            self.request_shutdown()

            print(
                "[SHUTDOWN] "
                "Trade active. Waiting for exit."
            )

            return

        # =====================================
        # TRIGGER ARMED
        # =====================================

        if state_machine.is_trigger_armed():

            print(
                "[SHUTDOWN] "
                "Cancelling trigger."
            )

            state_machine.reset()

        # =====================================
        # IDLE OR RESETTED
        # =====================================

        print(
            "[SHUTDOWN] "
            "Ready for shutdown."
        )

        self.shutdown()


shutdown_manager = ShutdownManager()
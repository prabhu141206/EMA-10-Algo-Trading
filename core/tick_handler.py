from core.state_machine import StateMachine
from core.candle_builder import CandleBuilder
from core.signal_engine import SignalEngine
from core.breakout_watcher import BreakoutWatcher
from trade_engine.virtual_trade_engine import VirtualTradeEngine
from system.shutdown_manager import shutdown_manager


class TickHandler:

    def __init__(self, option_ws, shutdown_manager):

        # ============================================
        # SINGLE STRATEGY COMPONENTS
        # ============================================

        self.shutdown_manager = shutdown_manager

        self.state_machine = StateMachine()

        self.candle_builder = CandleBuilder()

        self.engine = VirtualTradeEngine(
            option_ws,
            self.state_machine
        )

        self.signal_engine = SignalEngine(
            self.state_machine
        )

        self.breakout_watcher = BreakoutWatcher(
            self.engine,
            self.state_machine
        )

        self.first_candle_completed = False
    # ============================================
    # MAIN TICK FLOW
    # ============================================

    def handle_tick(self, tick):

        #print(f"[TICK] {tick['price']}")

        candle_closed, closed_candle = (
            self.candle_builder.add_tick(tick)
        )

        # ----------------------------------------
        # Candle Closed
        # ----------------------------------------

        if candle_closed:

            # =====================================
            # CHECK IF TIME IS UP
            # =====================================

            if self.shutdown_manager.is_time_to_shutdown():
                self.shutdown_manager.evaluate_strategy_state()
                return 

            # =====================================
            # INITIAL SYNCHRONIZATION
            # =====================================

            if not self.first_candle_completed:

                self.first_candle_completed = True

                print(
                    "[CANDLE] Synchronized "
                    "candle formation started"
                )

                return

            # =====================================
            # NORMAL CANDLE CLOSE
            # =====================================

            print("\n" + "=" * 60)
            print(
                f"[CANDLE CLOSED] "
                f"O={closed_candle['open']} "
                f"H={closed_candle['high']} "
                f"L={closed_candle['low']} "
                f"C={closed_candle['close']}"
            )

            

            if self.state_machine.is_trigger_armed():

                self.state_machine.expire_trigger()

            self.signal_engine.on_candle_close(
                closed_candle
            )

            if self.state_machine.is_trigger_armed():

                print(
                    f"[TRIGGER FORMED] "
                    f"{self.state_machine.direction} "
                    f"@ {self.state_machine.trigger_price}"
                )

            else:

                print("[TRIGGER] No setup")

            print(
                f"[STATE] "
                f"{self.state_machine.state}"
            )

            print("=" * 60)


            return
        # ----------------------------------------
        # Live Breakout Check
        # ----------------------------------------

        if self.state_machine.is_trigger_armed():

            self.breakout_watcher.check_tick(tick)

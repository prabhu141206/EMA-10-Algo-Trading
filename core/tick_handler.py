from core.state_machine import StateMachine
from core.candle_builder import CandleBuilder
from core.signal_engine import SignalEngine
from core.breakout_watcher import BreakoutWatcher
from trade_engine.virtual_trade_engine import VirtualTradeEngine


class TickHandler:

    def __init__(self, option_ws):

        # ============================================
        # SINGLE STRATEGY COMPONENTS
        # ============================================

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

    # ============================================
    # MAIN TICK FLOW
    # ============================================

    def handle_tick(self, tick):

        print(f"[TICK] {tick['price']}")

        candle_closed, closed_candle = (
            self.candle_builder.add_tick(tick)
        )

        # ----------------------------------------
        # Candle Closed
        # ----------------------------------------

        if candle_closed:

            print("[CANDLE CLOSED]")

            if self.state_machine.is_trigger_armed():
                self.state_machine.expire_trigger()

            self.signal_engine.on_candle_close(
                closed_candle
            )

            return

        # ----------------------------------------
        # Live Breakout Check
        # ----------------------------------------

        if self.state_machine.is_trigger_armed():

            self.breakout_watcher.check_tick(tick)
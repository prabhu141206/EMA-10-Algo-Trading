# strategy/strategy_instance.py

from core.state_machine import StateMachine
from core.candle_builder import CandleBuilder
from core.signal_engine import SignalEngine
from core.breakout_watcher import BreakoutWatcher
from trade_engine.virtual_trade_engine import VirtualTradeEngine


class StrategyInstance:

    def __init__(self, symbol, option_ws):
        """
        One COMPLETE isolated strategy.
        """

        self.symbol = symbol

        # Each strategy has its OWN components
        self.state_machine = StateMachine()

        self.candle_builder = CandleBuilder()

        # 🔴 FIX: pass state_machine into engine
        self.engine = VirtualTradeEngine(option_ws, self.state_machine)
        
        self.signal_engine = SignalEngine(self.state_machine)

        self.breakout_watcher = BreakoutWatcher(
            engine=self.engine,
            state_machine=self.state_machine
        )

    def handle_tick(self, tick: dict):

        candle_closed, closed_candle = self.candle_builder.add_tick(tick)

        #testing 4
        print(f"[INSTANCE {self.symbol}] price={tick['price']}")
        
        # Candle close logic
        if candle_closed:
            
            #testing 5
            print(f"[CANDLE CLOSED] {self.symbol}")

            if self.state_machine.is_trigger_armed():
                self.state_machine.expire_trigger()

            self.signal_engine.on_candle_close(closed_candle)
            return

        # Live tick breakout check
        if self.state_machine.is_trigger_armed():
            self.breakout_watcher.check_tick(tick)
# strategy/strategy_manager.py

from strategy.strategy_instance import StrategyInstance


class StrategyManager:

    def __init__(self, option_ws):
        """
        Manages multiple strategy instances.
        """

        self.option_ws = option_ws
        self.strategies = {}

    # =====================================================
    # REGISTER STRATEGY
    # =====================================================

    def add_strategy(self, symbol):

        strategy = StrategyInstance(
            symbol=symbol,
            option_ws=self.option_ws
        )

        self.strategies[symbol] = strategy

    # =====================================================
    # ROUTE TICKS TO CORRECT STRATEGY
    # =====================================================

    def route_tick(self, tick):

        symbol = tick["symbol"]

        strategy = self.strategies.get(symbol)

        if not strategy:
            print(f"[WARNING] No strategy for {symbol}")  # 🔴 DEBUG HELP
            return

        #testing 3
        print(f"[MANAGER] Routing to strategy: {symbol}")
        strategy.handle_tick(tick)
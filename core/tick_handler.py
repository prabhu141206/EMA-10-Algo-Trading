class TickHandler:

    def __init__(self, strategy_manager):
        self.strategy_manager = strategy_manager

    def handle_tick(self, tick: dict):

        if "symbol" not in tick:
            tick["symbol"] = "NSE:NIFTY50-INDEX"

        # testing where actually this routes goes (2)
        #print(f"[ROUTE] → {tick['symbol']}")

        self.strategy_manager.route_tick(tick)
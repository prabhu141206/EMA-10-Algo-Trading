
from utils.time_utils import epoch_to_ist
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import trade_entry



class BreakoutWatcher:

    def __init__(self, engine, state_machine):
        """
        No globals. Everything injected.
        """
        self.engine = engine
        self.state_machine = state_machine

    def check_tick(self, tick: dict):

        # If no trigger → do nothing
        if not self.state_machine.is_trigger_armed():
            return

        price = tick["price"]
        ts = tick["timestamp"]

        direction = self.state_machine.direction
        trigger_price = self.state_machine.trigger_price
        
        #testing 6
        #print(f"[BREAKOUT] {direction} @ {price}")
        
        # ================= BREAKOUT LOGIC =================
        if direction == "BUY" and price >= trigger_price:
            self._fire_entry(direction, trigger_price, ts)

        elif direction == "SELL" and price <= trigger_price:
            self._fire_entry(direction, trigger_price, ts)

    def _fire_entry(self, direction, trigger_price, ts):

        # Protection: already in trade
        if self.state_machine.is_in_trade():
            return

        # Protection: engine already active
        if self.engine.trade_active:
            return

        print(f"[ENTRY] 🚀 {direction} breakout at {trigger_price}")

        # Update state
        self.state_machine.enter_trade()

        # Start trade

        print("Breakout watcher")
        print('[DEBUG 1] called start_trade()')
        self.engine.start_trade(
            direction=direction,
            breakout_price=trigger_price,
            candle_time=ts
        )

  
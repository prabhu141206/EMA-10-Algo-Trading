from core.state_machine import state_machine
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
        print(f"[BREAKOUT] {direction} @ {price}")
        
        # ================= BREAKOUT LOGIC =================
        if direction == "BUY" and price >= trigger_price:
            self._fire_entry(direction, price, ts)

        elif direction == "SELL" and price <= trigger_price:
            self._fire_entry(direction, price, ts)

    def _fire_entry(self, direction, price, ts):

        # Protection: already in trade
        if self.state_machine.is_in_trade():
            return

        # Protection: engine already active
        if self.engine.trade_active:
            return

        print(f"[ENTRY] 🚀 {direction} breakout at {price}")

        # Update state
        self.state_machine.enter_trade()

        # Start trade
        self.engine.start_trade(
            direction=direction,
            spot_price=price,
            candle_time=ts
        )

        # Telegram alert
        telegram_alert.send(
            trade_entry(
                direction,
                price,
                self.state_machine.trigger_price,
                price + 20 if direction == "BUY" else price - 20,
                epoch_to_ist(ts)
            )
        )
from core.state_machine import state_machine
from utils.time_utils import epoch_to_ist
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import trade_entry


class BreakoutWatcher:

    def __init__(self, engine):
        self.engine = engine

    def check_tick(self, tick: dict):

        if not state_machine.is_trigger_armed():
            return

        price = tick["price"]
        ts = tick["timestamp"]

        direction = state_machine.direction
        trigger_price = state_machine.trigger_price

        if direction == "BUY" and price >= trigger_price:
            self._fire_entry(direction, price, ts)

        elif direction == "SELL" and price <= trigger_price:
            self._fire_entry(direction, price, ts)

    def _fire_entry(self, direction, price, ts):

        # Protection 1
        if state_machine.is_in_trade():
            return

        # Protection 2
        if self.engine.trade_active:
            return

        print(
            f"[ENTRY] 🚀 {direction} breakout at "
            f"{epoch_to_ist(ts)} | price={price}"
        )

        # Tell engine to start trade
        self.engine.start_trade(
            direction=direction,
            spot_price=price,
            candle_time=ts
        )

        # Now mark state
        state_machine.enter_trade()

        # Telegram alert
        telegram_alert.send(
            trade_entry(
                direction,
                price,
                state_machine.trigger_price,
                price + 20 if direction == "BUY" else price - 20,
                epoch_to_ist(ts)
            )
        )
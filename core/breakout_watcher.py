from core.state_machine import state_machine  
from utils.time_utils import epoch_to_ist
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import trade_entry
from trade_engine.virtual_trade_engine import VirtualTradeEngine
from trade_engine.option_ws import OptionWebSocket
from config.settings import ACCESS_TOKEN

engine = VirtualTradeEngine()


class BreakoutWatcher:
    def check_tick(self, tick: dict):
        if not state_machine.is_trigger_armed():
            return

        price = tick["price"]
        direction = state_machine.direction
        trigger_price = state_machine.trigger_price

        if direction == "BUY" and price >= trigger_price:
            self._fire_entry(direction, price, tick["timestamp"])

        elif direction == "SELL" and price <= trigger_price:
            self._fire_entry(direction, price, tick["timestamp"])
            

    def _fire_entry(self, direction, price, ts):

        # Hard protection
        if state_machine.is_in_trade():
            return

        if engine.trade_active:
            return

        print(
            f"[ENTRY] 🚀 {direction} breakout at "
            f"{epoch_to_ist(ts)} | price={price}"
        )

        # ✅ Only tell engine to start trade
        engine.start_trade(
            direction=direction,
            spot_price=price,
            candle_time=ts
        )

        # Mark state AFTER engine call
        state_machine.enter_trade()

        # Strategy-level telegram
        telegram_alert.send(
            trade_entry(
                direction,
                price,
                state_machine.trigger_price,
                price + 20 if direction == "BUY" else price - 20,
                epoch_to_ist(ts)
            )
        )





breakout_watcher = BreakoutWatcher()
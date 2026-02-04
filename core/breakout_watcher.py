from core.state_machine import state_machine
from utils.logger import log_event
from datetime import datetime
from core.paper_trade.paper_trade_engine import paper_trade_engine


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
        print(
            f"[ENTRY] 🚀 {direction} breakout at "
            f"{datetime.fromtimestamp(ts)} | price={price}"
        )

        # 1️⃣ LOG STRATEGY ENTRY
        log_event(
            event_type="ENTRY_FIRED",
            direction=direction,
            price=price,
            trigger_price=state_machine.trigger_price,
            candle_time=state_machine.trigger_time,
            note="Breakout confirmed"
        )

        # 2️⃣ START PAPER TRADE (🔥 THIS WAS MISSING)
        paper_trade_engine.enter_trade(
            direction=direction,
            index_price=price,        # index LTP
            option_entry_price=120,   # assumed ATM premium
            delta=0.5
        )

        # 3️⃣ MOVE TO IN_TRADE STATE
        state_machine.enter_trade()


breakout_watcher = BreakoutWatcher()

from core.state_machine import state_machine
from utils.logger import log_event
from utils.db_logger import db_logger   
from core.paper_trade.paper_trade_engine import paper_trade_engine
from utils.time_utils import epoch_to_ist
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import trade_entry

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
            f"{epoch_to_ist(ts)} | price={price}"
        )

        #  CSV STRATEGY EVENT LOG
        # ==================================================
        log_event(
            event_type="ENTRY_FIRED",
            direction=direction,
            price=price,
            trigger_price=state_machine.trigger_price,
            candle_time=state_machine.trigger_time,
            note="Breakout confirmed"
        )

       
        #  DATABASE STRATEGY EVENT LOG
        # ==================================================

        db_logger.log_trade_event(
            event_type="ENTRY_FIRED",
            direction=direction,
            price=price,
            trigger_price=state_machine.trigger_price,
            candle_time=state_machine.trigger_time,
            note="Breakout confirmed",
            ts=ts
        )

        #  START PAPER TRADE
        paper_trade_engine.enter_trade(
            direction=direction,
            index_price=price,
            option_entry_price=120,
            delta=0.5,
            ts = ts
        )


        # ---------- SENDING ALERTS ------------
        telegram_alert.send(
            trade_entry(
                direction,
                price,
                state_machine.trigger_price,
                price + 20 if direction == "BUY" else price - 20,
                epoch_to_ist(ts)
            )
        )

        

        #  MOVE TO IN_TRADE
        state_machine.enter_trade()


breakout_watcher = BreakoutWatcher()
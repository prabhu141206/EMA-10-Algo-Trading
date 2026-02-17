from core.state_machine import state_machine
from db.logger import db_logger   
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
        
        # HARD BLOCK: prevent multiple entries
        if state_machine.is_in_trade():
            return
        
        if engine.trade_active:
            return
        
        print(
            f"[ENTRY] 🚀 {direction} breakout at "
            f"{epoch_to_ist(ts)} | price={price}"
        )


        #  START PAPER TRADE
        engine.on_trigger(
                direction=direction,
                spot_price=price,
                candle_time=ts
        )

        # build option symbol
        option_symbol = engine.symbol

        option_ws = OptionWebSocket(
                    access_token=ACCESS_TOKEN,
                    symbol=option_symbol,
                    engine=engine
                )

        engine.attach_ws(option_ws)
        option_ws.connect()

       


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
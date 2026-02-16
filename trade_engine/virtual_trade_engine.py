from trade_engine.base_engine import BaseEngine
from options.symbol_builder import build_option_symbol
from options.symbol_formatter import format_symbol
from db.logger import db_logger
from utils.time_utils import epoch_to_ist

from alerts.telegram_alert import telegram_alert
from alerts.message_templates import option_entry_alert, option_exit_alert


class VirtualTradeEngine(BaseEngine):

    def __init__(self):
        self.trade_active = False
        self.direction = None
        self.symbol = None
        self.entry_price = None
        self.target = None
        self.sl = None
        self.entry_time = None
        self.ws = None
        self.index_price = None
        self.capital_used = None
        self.lot_size = 65      #Nifty 50 lot size

    # ========= RESET LOGIC =================
    def reset(self):
        self.trade_active = False
        self.direction = None
        self.symbol = None
        self.entry_price = None
        self.target = None
        self.sl = None
        self.entry_time = None
        self.index_price = None
        self.capital_used = None

    def attach_ws(self, ws):
        self.ws = ws

    # ========= DESCRIPTION HELPERS =================
    def get_trade_description(self, direction):
        if direction == "BUY":
            trend = "Upside Breakout"
            instrument = "Buy Call Option"
        else:
            trend = "Downside Breakout"
            instrument = "Buy Put Option"
        return trend, instrument

    def get_exit_description(self, reason, pnl):
        trend, instrument = self.get_trade_description(self.direction)

        if reason == "TARGET":
            result = "Target Hit 🎯"
        else:
            result = "Stop Loss Hit 🛑"

        if pnl >= 0:
            outcome = "Profit Booked"
        else:
            outcome = "Loss Booked"

        return trend, instrument, result, outcome

    # =========================
    # TRIGGER COMES FROM STRATEGY
    # =========================
    def on_trigger(self, direction, spot_price, candle_time):

        if self.trade_active:
            return

        self.direction = direction
        self.index_price = spot_price

        # FIXED: correct param name
        self.symbol = build_option_symbol(
            index_price=spot_price,
            direction=direction
        )

        self.entry_time = candle_time

        

        print("Selected Symbol:", self.symbol)

    # =========================
    # FIRST TICK = ENTRY
    # =========================
    def on_option_tick(self, price, bid, ask, ts):

        if self.symbol is None or self.direction is None:
            return

        # ===== ENTRY =====
        if not self.trade_active:
            self.entry_price = price
            self.trade_active = True

            self.capital_used = price * self.lot_size
            self.target = price + 20
            self.sl = price - 10

            entry_time = epoch_to_ist(ts)

            # ===== DB ENTRY LOG (FIXED FOR NEW TABLE STRUCTURE) =====
            db_logger.log_paper_trade_entry(
                symbol=self.symbol,
                direction=self.direction,
                index_price=self.index_price,
                entry_price=price,
                entry_time=entry_time,
                sl_price=self.sl,
                target_price=self.target,
                lot_size=self.lot_size,
                capital_used=self.capital_used,
                strategy_name="EMA10_BREAKOUT"
            )



            print("ENTRY @", price)

            # ===== TELEGRAM ENTRY ALERT =====
            trend, instrument = self.get_trade_description(self.direction)
            readable_symbol = format_symbol(self.symbol)
            capital_required = price * 65

            telegram_alert.send(
                option_entry_alert(
                    symbol=readable_symbol,
                    trend=trend,
                    instrument=instrument,
                    entry_price=price,
                    capital=capital_required,
                    target=self.target,
                    sl=self.sl,
                    time=entry_time
                )
            )

            return

        # =========================
        # CHECK EXIT CONDITIONS
        # =========================
        if price >= self.target:
            self._exit_trade("TARGET", price, ts)

        elif price <= self.sl:
            self._exit_trade("SL", price, ts)

    # =========================
    # EXIT LOGIC
    # =========================
    def _exit_trade(self, reason, price, ts):

        exit_time = epoch_to_ist(ts)

        if self.direction == "BUY":
            pnl = price - self.entry_price
        else:
            pnl = self.entry_price - price

        # ===== DB EXIT LOG (FIXED) =====
        db_logger.log_paper_trade_exit(
            symbol=self.symbol,
            exit_price=price,
            exit_time=exit_time,
            pnl=pnl,
            exit_reason=reason
        )

       

        

        print("EXIT:", reason, price)

        # ===== TELEGRAM EXIT ALERT (FIXED) =====
        trend, instrument, result, outcome = self.get_exit_description(reason, pnl)
        readable_symbol = format_symbol(self.symbol)

        telegram_alert.send(
            option_exit_alert(
                symbol=readable_symbol,
                trend=trend,
                instrument=instrument,
                exit_price=price,
                pnl=pnl * 65,
                reason=result,
                outcome=outcome,
                time=exit_time
            )
        )

        # ===== STOP WS STREAM =====
        if self.ws:
            try:
                self.ws.fyers.disconnect()
            except:
                try:
                    self.ws.fyers.close()
                except:
                    pass
            self.ws = None

        self.reset()

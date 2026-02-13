from trade_engine.base_engine import BaseEngine
from options.symbol_builder import build_option_symbol
from options.symbol_formatter import format_symbol

from utils.paper_logger import log_paper_trade
from db.logger import db_logger
from utils.logger import log_event
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

    # =========RESET LOGIC================
    def reset(self):
        self.trade_active = False
        self.direction = None
        self.symbol = None
        self.entry_price = None
        self.target = None
        self.sl = None
        self.entry_time = None
    
    def attach_ws(self, ws):
        self.ws = ws

    def get_exit_description(self, reason, pnl):
        """
        Builds human readable exit message context
        """

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

    def get_trade_description(self, direction):
        """
        Converts engine direction → human language
        """
        if direction == "BUY":
            trend = "Upside Breakout"
            instrument = "Buy Call Option"
        else:
            trend = "Downside Breakout"
            instrument = "Buy Put Option"

        return trend, instrument
    
    # =========================
    # TRIGGER COMES FROM STRATEGY
    # =========================
    def on_trigger(self, direction, spot_price, candle_time):

        if self.trade_active:
            return

        self.direction = direction

        # build CE/PE symbol
        self.symbol = build_option_symbol(
            spot_price=spot_price,
            direction=direction
        )

        self.entry_time = candle_time

        log_event(
            event_type="OPTION_SYMBOL_SELECTED",
            direction=direction,
            price=spot_price,
            note=self.symbol
        )

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

            self.target = price + 20
            self.sl = price - 10

            entry_time = epoch_to_ist(ts)

            # ===== DB LOG =====
            db_logger.log_paper_trade_entry(
                symbol=self.symbol,
                direction=self.direction,
                entry_price=price,
                entry_time=entry_time
            )

            # ===== PAPER LOG =====
            log_paper_trade(
                symbol=self.symbol,
                direction=self.direction,
                price=price,
                time=entry_time
            )

            # ===== EVENT =====
            log_event(
                event_type="OPTION_ENTRY",
                direction=self.direction,
                price=price,
                note=f"{self.symbol}"
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

        # ===== DB =====
        db_logger.log_paper_trade_exit(
            symbol=self.symbol,
            exit_price=price,
            exit_time=exit_time,
            pnl=pnl
        )

        # ===== PAPER LOG =====
        log_paper_trade(
            symbol=self.symbol,
            exit_price=price,
            time=exit_time,
            pnl=pnl
        )

        # ===== EVENT =====
        log_event(
            event_type="OPTION_EXIT",
            direction=self.direction,
            price=price,
            note=f"{reason} | {self.symbol}"
        )

        print("EXIT:", reason, price)

        # ===== TELEGRAM EXIT ALERT =====
        trend, instrument = self.get_exit_description(self.direction)
        readable_symbol = format_symbol(self.symbol)

        telegram_alert.send(
            option_exit_alert(
                symbol=readable_symbol,
                trend=trend,
                instrument=instrument,
                exit_price=price,
                pnl=pnl * 65,   # lot adjusted
                reason=reason,
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

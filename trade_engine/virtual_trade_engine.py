from trade_engine.base_engine import BaseEngine
from options.symbol_builder import build_option_symbol
from options.symbol_formatter import format_symbol
from db.logger import db_logger
from utils.time_utils import epoch_to_ist
from core.state_machine import state_machine
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import option_entry_alert, option_exit_alert


class VirtualTradeEngine(BaseEngine):

    def __init__(self, option_ws):
        self.option_ws = option_ws

        self.trade_active = False
        self.direction = None
        self.symbol = None
        self.entry_price = None
        self.target = None
        self.sl = None
        self.entry_time = None
        self.index_price = None
        self.capital_used = None
        self.lot_size = 65

    # ---------------------------------------------------
    # START TRADE
    # ---------------------------------------------------

    def start_trade(self, direction, spot_price, candle_time):

        if self.trade_active:
            return

        self.direction = direction
        self.index_price = spot_price
        self.entry_time = candle_time

        self.symbol = build_option_symbol(
            index_price=spot_price,
            direction=direction
        )

        print("Selected Symbol:", self.symbol)

        # 🔥 Only subscribe — do NOT create socket
        self.option_ws.subscribe(self.symbol, self)

    # ---------------------------------------------------
    # OPTION TICK
    # ---------------------------------------------------

    def on_option_tick(self, price, bid, ask, ts):

        if not self.direction:
            return

        # ENTRY
        if not self.trade_active:

            self.entry_price = price
            self.trade_active = True

            self.capital_used = price * self.lot_size
            self.target = price + 20
            self.sl = price - 10

            entry_time = epoch_to_ist(ts)

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

            trend = "Upside Breakout" if self.direction == "BUY" else "Downside Breakout"
            instrument = "Buy Call Option" if self.direction == "BUY" else "Buy Put Option"

            telegram_alert.send(
                option_entry_alert(
                    symbol=format_symbol(self.symbol),
                    trend=trend,
                    instrument=instrument,
                    entry_price=price,
                    capital=self.capital_used,
                    target=self.target,
                    sl=self.sl,
                    time=entry_time
                )
            )

            return

        # EXIT
        if price >= self.target:
            self._exit_trade("TARGET", price, ts)

        elif price <= self.sl:
            self._exit_trade("SL", price, ts)

    # ---------------------------------------------------
    # EXIT
    # ---------------------------------------------------

    def _exit_trade(self, reason, price, ts):

        if not self.trade_active:
            return

        self.trade_active = False

        exit_time = epoch_to_ist(ts)

        pnl_points = (
            price - self.entry_price
            if self.direction == "BUY"
            else self.entry_price - price
        )

        pnl = pnl_points * self.lot_size

        db_logger.log_paper_trade_exit(
            symbol=self.symbol,
            exit_price=price,
            exit_time=exit_time,
            pnl=pnl,
            exit_reason=reason
        )

        print("EXIT:", reason, price)

        telegram_alert.send(
            option_exit_alert(
                symbol=format_symbol(self.symbol),
                trend="Trade Exit",
                instrument="",
                exit_price=price,
                pnl=pnl,
                reason=reason,
                outcome="🟢 Profit" if pnl >= 0 else "🔴 Loss",
                time=exit_time
            )
        )

        # 🔥 Only unsubscribe — do NOT close socket
        self.option_ws.unsubscribe()

        state_machine.reset()
        self._reset_internal()

    def _reset_internal(self):
        self.direction = None
        self.symbol = None
        self.entry_price = None
        self.target = None
        self.sl = None
        self.entry_time = None
        self.index_price = None
        self.capital_used = None
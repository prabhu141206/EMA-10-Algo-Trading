from trade_engine.base_engine import BaseEngine
from options.symbol_builder import build_option_symbol
from options.symbol_formatter import format_symbol
from db.logger import db_logger
from utils.time_utils import epoch_to_ist
from core.state_machine import state_machine
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
        self.lot_size = 65

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

    def get_trade_description(self, direction):
        if direction == "BUY":
            return "Upside Breakout", "Buy Call Option"
        else:
            return "Downside Breakout", "Buy Put Option"

    def get_exit_description(self, reason, pnl):
        trend, instrument = self.get_trade_description(self.direction)

        result = "Target Hit 🎯" if reason == "TARGET" else "Stop Loss Hit 🛑"
        outcome = "🟢 Profit Booked" if pnl >= 0 else "🔴 Loss Booked"

        return trend, instrument, result, outcome

    # =============================
    # TRIGGER
    # =============================

    def on_trigger(self, direction, spot_price, candle_time):

        if self.trade_active:
            return

        self.direction = direction
        self.index_price = spot_price

        self.symbol = build_option_symbol(
            index_price=spot_price,
            direction=direction
        )

        self.entry_time = candle_time

        print("Selected Symbol:", self.symbol)

    # =============================
    # OPTION TICK
    # =============================

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

            trend, instrument = self.get_trade_description(self.direction)
            readable_symbol = format_symbol(self.symbol)

            telegram_alert.send(
                option_entry_alert(
                    symbol=readable_symbol,
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

        # ===== EXIT CHECK =====

        if price >= self.target:
            self._exit_trade("TARGET", price, ts)

        elif price <= self.sl:
            self._exit_trade("SL", price, ts)

    # =============================
    # EXIT
    # =============================

    def _exit_trade(self, reason, price, ts):

        if not self.trade_active:
            return

        self.trade_active = False

        exit_time = epoch_to_ist(ts)

        if self.direction == "BUY":
            pnl_points = price - self.entry_price
        else:
            pnl_points = self.entry_price - price

        pnl = pnl_points * self.lot_size

        db_logger.log_paper_trade_exit(
            symbol=self.symbol,
            exit_price=price,
            exit_time=exit_time,
            pnl=pnl,
            exit_reason=reason
        )

        print("EXIT:", reason, price)

        trend, instrument, result, outcome = self.get_exit_description(reason, pnl)
        readable_symbol = format_symbol(self.symbol)

        telegram_alert.send(
            option_exit_alert(
                symbol=readable_symbol,
                trend=trend,
                instrument=instrument,
                exit_price=price,
                pnl=pnl,
                reason=result,
                outcome=outcome,
                time=exit_time
            )
        )

        # Proper WebSocket close
        if self.ws:
            try:
                self.ws.fyers.disconnect()
            except Exception as e:
                print("WS close error:", e)

            self.ws = None

        state_machine.reset()
        self.reset() 
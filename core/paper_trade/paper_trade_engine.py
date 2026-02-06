from utils.paper_logger import log_paper_trade
from db.logger import db_logger
from utils.time_utils import epoch_to_ist
from core.state_machine import state_machine
from utils.logger import log_event
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import trade_exit, paper_trade_entry


class PaperTradeEngine:

    def __init__(self):
        self.reset()

    def reset(self):
        self.in_trade = False

        self.direction = None
        self.index_entry_price = None
        self.option_entry_price = None

        self.delta = None
        self.sl = None
        self.target = None

        self.trade_id = None   # ✅ IMPORTANT (Lifecycle tracking)

    # --------------------------------------------------
    # ENTRY
    # --------------------------------------------------
    def enter_trade(
        self,
        direction: str,
        index_price: float,
        option_entry_price: float = 120.0,
        delta: float = 0.5,
        ts: int = None
    ):

        self.in_trade = True
        self.direction = direction

        self.index_entry_price = index_price
        self.option_entry_price = option_entry_price
        self.delta = delta

        if direction == "BUY":
            self.sl = option_entry_price - 10
            self.target = option_entry_price + 20
        else:
            self.sl = option_entry_price + 10
            self.target = option_entry_price - 20

        # -------- CSV LOG --------
        log_paper_trade(
            event="ENTRY",
            direction=direction,
            entry_price=option_entry_price,
            current_price=option_entry_price,
            sl=self.sl,
            target=self.target,
            pnl=0,
            note=f"Delta={delta}"
        )

        # -------- DB INSERT --------
        self.trade_id = db_logger.log_paper_trade_entry(
            entry_time=epoch_to_ist(ts),
            direction=direction,
            entry_price=option_entry_price,
            sl_price=self.sl,
            target_price=self.target
        )


        # ---------- SENDING ALERTS ------------
        telegram_alert.send(
            paper_trade_entry(
                direction,
                option_entry_price,
                self.sl,
                self.target,
                delta
            )
        )

    # --------------------------------------------------
    # TICK UPDATE
    # --------------------------------------------------
    def on_index_tick(self, index_ltp: float, ts: int):

        if not self.in_trade:
            return

        index_move = index_ltp - self.index_entry_price
        option_move = index_move * self.delta

        if self.direction == "BUY":
            option_price = self.option_entry_price + option_move
            pnl = option_price - self.option_entry_price
        else:
            option_price = self.option_entry_price - option_move
            pnl = self.option_entry_price - option_price

        # TARGET HIT
        if (
            self.direction == "BUY" and option_price >= self.target
        ) or (
            self.direction == "SELL" and option_price <= self.target
        ):
            self._exit("TARGET", option_price, pnl, ts)
            return

        # STOPLOSS HIT
        if (
            self.direction == "BUY" and option_price <= self.sl
        ) or (
            self.direction == "SELL" and option_price >= self.sl
        ):
            self._exit("STOPLOSS", option_price, pnl, ts)

    # --------------------------------------------------
    # EXIT
    # --------------------------------------------------
    def _exit(self, reason, price, pnl, ts):

        # -------- CSV LOG --------
        log_paper_trade(
            event=reason,
            direction=self.direction,
            entry_price=self.option_entry_price,
            current_price=price,
            sl=self.sl,
            target=self.target,
            pnl=round(pnl, 2),
            note="Delta-based exit"
        )

        # -------- EVENT CSV --------
        log_event(
            event_type="EXIT_FIRED",
            direction=self.direction,
            price=price,
            trigger_price=state_machine.trigger_price,
            candle_time=state_machine.trigger_time,
            note="Paper trade exit"
        )

        # -------- DB UPDATE --------
        db_logger.log_paper_trade_exit(
            trade_id=self.trade_id,
            exit_time=epoch_to_ist(ts),
            exit_price=price,
            pnl=round(pnl, 2)
        )

        # -------- EVENT DB --------
        db_logger.log_trade_event(
            event_type="EXIT_FIRED",
            direction=self.direction,
            price=price,
            trigger_price=state_machine.trigger_price,
            candle_time=state_machine.trigger_time,
            note="Paper trade exit",
            ts=ts
        )

        # ---------- SENDING ALERTS ------------

        telegram_alert.send(
            trade_exit(
                self.direction,
                price,
                pnl,
                reason,
                epoch_to_ist(ts)
            )
        )
        self.reset()


paper_trade_engine = PaperTradeEngine()
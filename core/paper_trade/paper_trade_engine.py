# core/paper_trade/paper_trade_engine.py

from utils.paper_logger import log_paper_trade


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

    # --------------------------------------------------
    # ENTRY
    # --------------------------------------------------
    def enter_trade(
        self,
        direction: str,
        index_price: float,
        option_entry_price: float = 120.0,
        delta: float = 0.5
    ):
        """
        Called ONCE when breakout happens
        """

        self.in_trade = True
        self.direction = direction

        self.index_entry_price = index_price
        self.option_entry_price = option_entry_price
        self.delta = delta

        # Fixed rules (your choice)
        if direction == "BUY":
            self.sl = option_entry_price - 10
            self.target = option_entry_price + 20
        else:
            self.sl = option_entry_price + 10
            self.target = option_entry_price - 20

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

    # --------------------------------------------------
    # TICK UPDATE
    # --------------------------------------------------
    def on_index_tick(self, index_ltp: float):
        """
        Called on EVERY index tick AFTER entry
        """

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
            self._exit("TARGET", option_price, pnl)
            return

        # STOP LOSS HIT
        if (
            self.direction == "BUY" and option_price <= self.sl
        ) or (
            self.direction == "SELL" and option_price >= self.sl
        ):
            self._exit("STOPLOSS", option_price, pnl)

    # --------------------------------------------------
    # EXIT
    # --------------------------------------------------
    def _exit(self, reason, price, pnl):
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

        self.reset()


# SINGLE INSTANCE
paper_trade_engine = PaperTradeEngine()

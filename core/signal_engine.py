from core.indicators import ema_10


class SignalEngine:
    def __init__(self, state_machine):
        """
        Each strategy gets its own SignalEngine
        tied to its own state machine.
        """
        self.state_machine = state_machine
        self.prev_ema = None  # EMA of previous candle

    def on_candle_close(self, candle: dict):

        if self.state_machine.is_in_trade():
            print("[SKIP] Already in trade → ignoring new setup")
            return

        open_ = candle["open"]
        high = candle["high"]
        low = candle["low"]
        close = candle["close"]

        # Compute EMA for current candle
        ema_now = ema_10.update(close)
        candle["ema"] = ema_now

        # First candle → no comparison possible
        if self.prev_ema is None:
            self.prev_ema = ema_now
            return

        # ================= BUY CONDITION =================
        if (
            close > self.prev_ema and   # uptrend
            close < open_ and           # red candle
            low > self.prev_ema         # no EMA touch
        ):
            self.state_machine.arm_trigger(
                direction="BUY",
                trigger_price=high,
                trigger_time=candle["timestamp"]
            )

        # ================= SELL CONDITION =================
        elif (
            close < self.prev_ema and
            close > open_ and
            high < self.prev_ema
        ):
            self.state_machine.arm_trigger(
                direction="SELL",
                trigger_price=low,
                trigger_time=candle["timestamp"]
            )

        # Store EMA for next candle
        self.prev_ema = ema_now

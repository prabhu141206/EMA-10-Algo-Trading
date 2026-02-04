from core.indicators import ema_10
from core.state_machine import state_machine


class SignalEngine:
    def __init__(self):
        self.prev_ema = None  # EMA from previous candle only

    def on_candle_close(self, candle: dict):
        open_ = candle["open"]
        high = candle["high"]
        low = candle["low"]
        close = candle["close"]

        # 1️⃣ Compute EMA but DO NOT use it yet
        ema_now = ema_10.update(close)
        candle["ema"] = ema_now

        # First candle → no previous EMA to compare with
        if self.prev_ema is None:
            self.prev_ema = ema_now
            return

        # ================= BUY (Design A) =================
        if (
            close > self.prev_ema and     # trend up (based on OLD EMA)
            close < open_ and             # red candle
            low > self.prev_ema           # no EMA touch
        ):
            state_machine.arm_trigger(
                direction="BUY",
                trigger_price=high,
                trigger_time=candle["timestamp"]
            )

        # ================= SELL (Design A) =================
        elif (
            close < self.prev_ema and     # trend down
            close > open_ and             # green candle
            high < self.prev_ema          # no EMA touch
        ):
            state_machine.arm_trigger(
                direction="SELL",
                trigger_price=low,
                trigger_time=candle["timestamp"]
            )

        # 4️⃣ Store EMA for NEXT candle
        self.prev_ema = ema_now


signal_engine = SignalEngine()

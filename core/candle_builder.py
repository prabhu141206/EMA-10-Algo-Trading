from core.state_machine import state_machine
from utils.time_utils import epoch_to_ist


class CandleBuilder:
    def __init__(self, timeframe_minutes: int = 5):
        """
        Each strategy must have its own CandleBuilder.
        """
        self.tf_seconds = timeframe_minutes * 60
        self.current_bucket = None
        self.current_candle = None

    def _get_bucket_start(self, ts: int) -> int:
        return ts - (ts % self.tf_seconds)

    def add_tick(self, tick: dict):

        price = tick["price"]
        ts = tick["timestamp"]

        bucket = self._get_bucket_start(ts)

        # First tick initialization
        if self.current_bucket is None:
            self.current_bucket = bucket
            return False, None

        # New candle formed
        if bucket != self.current_bucket:
            closed_candle = self.current_candle

            self.current_bucket = bucket
            self.current_candle = {
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "timestamp": bucket
            }

            return True, closed_candle

        # Update existing candle
        if self.current_candle is None:
            self.current_candle = {
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "timestamp": bucket
            }
            return False, None

        self.current_candle["high"] = max(self.current_candle["high"], price)
        self.current_candle["low"] = min(self.current_candle["low"], price)
        self.current_candle["close"] = price

        return False, None
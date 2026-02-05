# core/candle_builder.py

import datetime
from core.state_machine import state_machine
from utils.time_utils import epoch_to_ist

class CandleBuilder:
    def __init__(self, timeframe_minutes: int = 5):
        self.tf_seconds = timeframe_minutes * 60

        self.current_bucket = None
        self.current_candle = None

        # Startup / activation flags
        self.startup_log_printed = False
        self.system_activated = False

    def _get_bucket_start(self, ts: int) -> int:
        """Floor timestamp to 5-minute boundary"""
        return ts - (ts % self.tf_seconds)

    def add_tick(self, tick: dict):
        """
        Called on EVERY tick.
        Returns:
        (candle_closed: bool, closed_candle: dict | None)
        """

        price = tick["price"]
        ts = tick["timestamp"]
        
        if ts < 1600000000 :
            return False, None

        bucket = self._get_bucket_start(ts)

        # --------------------------------------------------
        # STARTUP PHASE: waiting for first valid 5-min bucket
        # --------------------------------------------------
        if self.current_bucket is None:
            self.current_bucket = bucket

            if not self.startup_log_printed:
                next_boundary = bucket + self.tf_seconds
                human_time = epoch_to_ist(next_boundary)
                print(
                    f"[INIT] Waiting for next full "
                    f"{self.tf_seconds // 60}-minute candle at {human_time}",
                    "\n"
                )
                self.startup_log_printed = True

            return False, None

        # --------------------------------------------------
        # NEW BUCKET → close previous candle
        # --------------------------------------------------
        if bucket != self.current_bucket:
            closed_candle = self.current_candle

            # Start new candle
            self.current_bucket = bucket
            self.current_candle = {
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "timestamp": bucket 
            }

            # 🔑 ACTIVATE SYSTEM EXACTLY ONCE
            if not self.system_activated:
                human_time = datetime.datetime.fromtimestamp(bucket)
                print(f"[CANDLE] First valid candle started at {human_time} \n")

                state_machine.activate_system()
                self.system_activated = True

                # Ignore the candle we woke up inside
                return False, None

            return True, closed_candle

        # --------------------------------------------------
        # SAME BUCKET → update OHLC
        # --------------------------------------------------
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


# SINGLE GLOBAL INSTANCE (do NOT change this)
candle_builder = CandleBuilder(timeframe_minutes=5)

# =========================================================
# CANDLE BUILDER
# =========================================================
#
# Responsibility:
# - Build 5-minute OHLC candles from live ticks
# - Detect candle completion
# - Return completed candle to TickHandler
#
# NOTE:
# SmartAPI provides only LTP.
# This class constructs OHLC from live prices.
#
# =========================================================

from datetime import datetime, timedelta


class CandleBuilder:

    def __init__(self, timeframe_minutes: int = 5):

        self.tf_seconds = timeframe_minutes * 60

        self.current_bucket = None
        self.current_candle = None

        now = datetime.now()

        next_boundary = (
            now.replace(second=0, microsecond=0)
            + timedelta(
                minutes=timeframe_minutes - (now.minute % timeframe_minutes)
            )
        )

        print(
            f"[CANDLE] Waiting for next "
            f"{timeframe_minutes}-minute boundary "
            f"({next_boundary.strftime('%H:%M')})"
        )

    # =====================================================
    # GET CANDLE BUCKET
    # =====================================================

    def _get_bucket_start(self, ts: int):

        return ts - (ts % self.tf_seconds)

    # =====================================================
    # PROCESS LIVE TICK
    # =====================================================

    def add_tick(self, tick: dict):

        price = tick["price"]
        ts = tick["timestamp"] // 1000

        bucket = self._get_bucket_start(ts)

        # -------------------------------------------------
        # FIRST TICK
        # -------------------------------------------------

        if self.current_bucket is None:

            self.current_bucket = bucket

            self.current_candle = {

                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "timestamp": bucket

            }

            return False, None

        # -------------------------------------------------
        # CANDLE COMPLETED
        # -------------------------------------------------

        if bucket != self.current_bucket:

            print(
                f"Bucket Changed : "
                f"{self.current_bucket} --> {bucket}"
            )

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

        # -------------------------------------------------
        # UPDATE LIVE CANDLE
        # -------------------------------------------------

        self.current_candle["high"] = max(
            self.current_candle["high"],
            price
        )

        self.current_candle["low"] = min(
            self.current_candle["low"],
            price
        )

        self.current_candle["close"] = price

        return False, None
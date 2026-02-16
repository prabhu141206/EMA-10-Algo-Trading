from datetime import datetime, time as dt_time, timezone, timedelta
import time

IST = timezone(timedelta(hours=5, minutes=30))

MARKET_START = dt_time(9, 15)
MARKET_END   = dt_time(15, 30)
ENTRY_CUTOFF = dt_time(15, 15)

def epoch_to_ist(epoch_seconds: int) -> datetime:
    return datetime.fromtimestamp(epoch_seconds, tz=IST)

def epoch_to_ist_time(epoch_seconds: int):
    return epoch_to_ist(epoch_seconds).time()

def is_market_open(epoch_seconds: int) -> bool:
    t = epoch_to_ist_time(epoch_seconds)
    return MARKET_START <= t <= MARKET_END

def is_entry_allowed(epoch_seconds: int) -> bool:
    t = epoch_to_ist_time(epoch_seconds)
    return MARKET_START <= t <= ENTRY_CUTOFF

FIVE_MIN = 5 * 60

def floor_to_5min(ts: int) -> int:
    return ts - (ts % FIVE_MIN)

def next_5min_boundary(ts: int) -> int:
    return ((ts // FIVE_MIN) + 1) * FIVE_MIN

def is_5min_boundary(ts: int) -> bool:
    return ts % FIVE_MIN == 0

def wait_until_market_open():
    while True:
        now_epoch = int(time.time())

        if is_market_open(now_epoch):
            print("[SCHEDULER] Market open. Starting system.")
            return

        time.sleep(20)
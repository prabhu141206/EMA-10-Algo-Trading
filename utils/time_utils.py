from datetime import datetime, time, timezone, timedelta

# ===============================
# EXCHANGE TIMEZONE
# ===============================

IST = timezone(timedelta(hours=5, minutes=30))


# ===============================
# MARKET TIMINGS (IST)
# ===============================

MARKET_START = time(9, 15)
MARKET_END = time(15, 30)
ENTRY_CUTOFF = time(15, 15)


# ===============================
# CORE CONVERTERS
# ===============================

def epoch_to_ist(epoch_seconds: int) -> datetime:
    """
    Convert broker epoch timestamp (UTC) → IST datetime
    """
    return datetime.fromtimestamp(epoch_seconds, tz=IST)


def epoch_to_ist_time(epoch_seconds: int) -> time:
    """
    Return ONLY IST time component
    """
    return epoch_to_ist(epoch_seconds).time()


# ===============================
# MARKET CHECKS
# ===============================

def is_market_open(epoch_seconds: int) -> bool:
    t = epoch_to_ist_time(epoch_seconds)
    return MARKET_START <= t <= MARKET_END


def is_entry_allowed(epoch_seconds: int) -> bool:
    t = epoch_to_ist_time(epoch_seconds)
    return MARKET_START <= t <= ENTRY_CUTOFF


# ===============================
# 5-MINUTE BUCKET HELPERS
# ===============================

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
        time.sleep(30)
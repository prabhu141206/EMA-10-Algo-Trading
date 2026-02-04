import datetime

MARKET_START = datetime.time(9, 15)
MARKET_END = datetime.time(15, 30)

ENTRY_CUTOFF = datetime.time(15, 15)


def epoch_to_time(epoch_seconds: int) -> datetime.time:
    dt = datetime.datetime.fromtimestamp(epoch_seconds)
    return dt.time()


def is_market_open(epoch_seconds: int) -> bool:
    t = epoch_to_time(epoch_seconds)
    return MARKET_START <= t <= MARKET_END


def is_entry_allowed(epoch_seconds: int) -> bool:
    t = epoch_to_time(epoch_seconds)
    return MARKET_START <= t <= ENTRY_CUTOFF


# utils/time_utils.py

FIVE_MIN = 5 * 60  # 300 seconds


def floor_to_5min(ts: int) -> int:
    """Floor timestamp to nearest lower 5-min boundary"""
    return ts - (ts % FIVE_MIN)


def next_5min_boundary(ts: int) -> int:
    """Next 5-min boundary strictly after ts"""
    return ((ts // FIVE_MIN) + 1) * FIVE_MIN


def is_5min_boundary(ts: int) -> bool:
    """True if ts is exactly on 5-min boundary"""
    return ts % FIVE_MIN == 0

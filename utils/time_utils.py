import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

MARKET_START = datetime.time(9, 15)
MARKET_END = datetime.time(15, 30)
ENTRY_CUTOFF = datetime.time(15, 15)


def epoch_to_ist(epoch_seconds: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(epoch_seconds, IST)


def epoch_to_time(epoch_seconds: int) -> datetime.time:
    return epoch_to_ist(epoch_seconds).time()


def is_market_open(epoch_seconds: int) -> bool:
    t = epoch_to_time(epoch_seconds)
    return MARKET_START <= t <= MARKET_END


def is_entry_allowed(epoch_seconds: int) -> bool:
    t = epoch_to_time(epoch_seconds)
    return MARKET_START <= t <= ENTRY_CUTOFF
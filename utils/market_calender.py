# utils/market_calendar.py

from datetime import date
from utils.holidays import MARKET_HOLIDAYS



def is_market_day(check_date: date) -> bool:

    # Saturday (5) and Sunday (6)
    if check_date.weekday() >= 5:
        return False

    # Trading Holiday
    if check_date in MARKET_HOLIDAYS:
        return False

    return True
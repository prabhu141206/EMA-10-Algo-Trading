from datetime import datetime, timedelta,time
from utils.market_calender import is_market_day


TRADING_START_TIME = time(hour=9, minute=15)

def get_next_start_time():

    current = datetime.now()

    # Start checking from tomorrow
    next_date = current.date() + timedelta(days=1)

    # Find the next trading day
    while not is_market_day(next_date):
        next_date += timedelta(days=1)

    # Combine date + trading start time
    next_start = datetime.combine(
        next_date,
        TRADING_START_TIME
    )

    # Calculate waiting time
    waiting_seconds = (next_start - current).total_seconds()

    return current, next_start, waiting_seconds
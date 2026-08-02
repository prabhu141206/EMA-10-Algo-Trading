from datetime import datetime, time

from utils.market_calender import is_market_day


MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)


def get_market_status():

    current = datetime.now()

    # Holiday / Weekend
    if not is_market_day(current.date()):
        return False, 0

    current_time = current.time()

    # Market Live
    if MARKET_OPEN <= current_time < MARKET_CLOSE:
        return True, 0

    # Before Market Opens
    if current_time < MARKET_OPEN:

        market_open = datetime.combine(
            current.date(),
            MARKET_OPEN
        )

        waiting_seconds = (
            market_open - current
        ).total_seconds()

        return False, waiting_seconds

    # After Market Close
    return False, 0
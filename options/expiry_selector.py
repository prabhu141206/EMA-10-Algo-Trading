from datetime import datetime, timedelta
import pytz

def get_nearest_expiry():
    ist = pytz.timezone("Asia/Kolkata")
    today = datetime.now(ist)

    # Tuesday = 1
    days_ahead = 1 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7

    expiry = today + timedelta(days=days_ahead)

    return expiry.strftime("%y%b").upper()
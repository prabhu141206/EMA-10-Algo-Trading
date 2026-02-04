import csv
import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "trade_events.csv")

HEADERS = [
    "timestamp",
    "event_type",
    "direction",
    "price",
    "trigger_price",
    "candle_time",
    "note"
]


def log_event(
    event_type,
    direction="",
    price="",
    trigger_price="",
    candle_time="",
    note=""
):
    # Ensure logs directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        # ✅ Write header only once
        if not file_exists:
            writer.writerow(HEADERS)

        # Write actual event row
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            event_type,
            direction,
            price,
            trigger_price,
            candle_time,
            note
        ])

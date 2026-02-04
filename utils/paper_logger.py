# utils/paper_logger.py

import csv
import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "paper_trades.csv")

HEADERS = [
    "timestamp",
    "event",
    "direction",
    "entry_price",
    "current_price",
    "sl",
    "target",
    "pnl",
    "note"
]


def log_paper_trade(
    event,
    direction,
    entry_price,
    current_price,
    sl,
    target,
    pnl,
    note=""
):
    os.makedirs(LOG_DIR, exist_ok=True)
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(HEADERS)

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            event,
            direction,
            entry_price,
            current_price,
            sl,
            target,
            pnl,
            note
        ])

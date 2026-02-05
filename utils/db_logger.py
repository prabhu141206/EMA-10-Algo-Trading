from utils.db import get_connection
from datetime import datetime
from time_utils import epoch_to_ist

class DBLogger:

    # ===== TRADE EVENTS =====
    def log_trade_event(self, event_type, direction, price,
                        trigger_price, candle_time, note, ts):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO trade_events
            (timestamp, event_type, direction, price, trigger_price, candle_time, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            epoch_to_ist(ts),
            event_type,
            direction,
            price,
            trigger_price,
            candle_time,
            note
        ))

        conn.commit()
        cursor.close()
        conn.close()


    def log_paper_trade_entry(self, entry_time, direction, entry_price,
                          sl_price, target_price):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO paper_trades
            (entry_time, direction, entry_price, sl_price, target_price)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            entry_time,
            direction,
            entry_price,
            sl_price,
            target_price
        ))

        trade_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return trade_id
    

    def log_paper_trade_exit(self, trade_id, exit_time, exit_price, pnl):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE paper_trades
            SET exit_time=%s, exit_price=%s, pnl=%s
            WHERE id=%s
        """, (
            exit_time,
            exit_price,
            pnl,
            trade_id
        ))

        conn.commit()
        cursor.close()
        conn.close()


# ⭐ global object
db_logger = DBLogger()
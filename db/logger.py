from db.queue import db_queue
from utils.time_utils import epoch_to_ist


#_________________This becomes the single entry point for database logging._________________________________

class DBLogger:

    def log_trade_event(self, event_type, direction,
                        price, trigger_price,
                        candle_time, note, ts):

        query = """
        INSERT INTO trade_events
        (timestamp, event_type, direction, price,
         trigger_price, candle_time, note)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            epoch_to_ist(ts),
            event_type,
            direction,
            price,
            trigger_price,
            candle_time,
            note
        )

        db_queue.put({
            "query": query,
            "values": values
        })


    def log_paper_entry(self, entry_time, direction,
                         entry_price, sl_price, target_price):

        query = """
        INSERT INTO paper_trades
        (entry_time, direction, entry_price, sl_price, target_price)
        VALUES (%s,%s,%s,%s,%s)
        """

        values = (
            entry_time,
            direction,
            entry_price,
            sl_price,
            target_price
        )

        db_queue.put({
            "query": query,
            "values": values
        })


    def log_paper_exit(self, exit_time, exit_price, pnl):

        query = """
        UPDATE paper_trades
        SET exit_time=%s, exit_price=%s, pnl=%s
        WHERE exit_time IS NULL
        """

        values = (
            exit_time,
            exit_price,
            pnl
        )

        db_queue.put({
            "query": query,
            "values": values
        })


db_logger = DBLogger()
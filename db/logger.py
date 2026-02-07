from db.queue import db_queue
from utils.time_utils import epoch_to_ist


#_________________This becomes the single entry point for database logging._________________________________

class DBLogger:

    def log_trade_event(self, event_type, direction,
                        price, trigger_price,
                        candle_time, note, ts):

        try:
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

        except Exception as e:
            print("DB ERROR (trade_events): ",e)
    


    def log_paper_trade_entry(self, entry_time, direction,
                         entry_price, sl_price, target_price):

        try:
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

        except Exception as e:
            print("DB ERROR (paper_trades): ",e)


    def log_paper_trade_exit(self, exit_time, exit_price, pnl):

        try:
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

        except Exception as e:
            print("DB ERROR (paper_trades): ",e)


db_logger = DBLogger()
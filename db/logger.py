from db.queue import db_queue
from utils.time_utils import epoch_to_ist


class DBLogger:

    # ==============================
    # ENTRY LOG
    # ==============================
    def log_paper_trade_entry(
        self,
        symbol,
        direction,
        index_price,
        entry_price,
        entry_time,
        sl_price,
        target_price,
        lot_size,
        capital_used,
        strategy_name
    ):
        
        try:
            query = """
            INSERT INTO trades
            (
                symbol,
                strategy_name,
                direction,
                index_price,
                entry_price,
                entry_time,
                sl_price,
                target_price,
                lot_size,
                capital_used
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            values = (
                symbol,
                strategy_name,
                direction,
                index_price,
                entry_price,
                entry_time,
                sl_price,
                target_price,
                lot_size,
                capital_used
            )

            db_queue.put({
                "query": query,
                "values": values
            })

        except Exception as e:
            print("DB ERROR (ENTRY):", e)

    # ==============================
    # EXIT LOG
    # ==============================
    def log_paper_trade_exit(
        self,
        symbol,
        exit_price,
        exit_time,
        pnl,
        exit_reason
    ):
        try:
            query = """
            UPDATE trades
            SET
                exit_price=%s,
                exit_time=%s,
                exit_reason=%s,
                pnl=%s
            WHERE symbol=%s
            AND exit_time IS NULL
            """

            values = (
                exit_price,
                exit_time,
                exit_reason,
                pnl,
                symbol
            )

            db_queue.put({
                "query": query,
                "values": values
            })

        except Exception as e:
            print("DB ERROR (EXIT):", e)


db_logger = DBLogger()
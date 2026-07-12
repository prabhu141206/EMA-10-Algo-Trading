from db.queue import db_queue


class DBLogger:

    # =====================================================
    # LOG TRADE ENTRY
    # =====================================================

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

        query = """
        INSERT INTO trades (
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
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
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

        try:

            db_queue.put({
                "query": query,
                "values": values
            })

        except Exception as e:

            print(f"[DB LOGGER] Failed to enqueue trade entry: {e}")

    # =====================================================
    # LOG TRADE EXIT
    # =====================================================

    def log_paper_trade_exit(
        self,
        symbol,
        exit_price,
        exit_time,
        pnl,
        exit_reason
    ):

        query = """
        UPDATE trades
        SET
            exit_price = %s,
            exit_time = %s,
            exit_reason = %s,
            pnl = %s
        WHERE
            symbol = %s
            AND exit_time IS NULL
        """

        values = (
            exit_price,
            exit_time,
            exit_reason,
            pnl,
            symbol
        )

        try:

            db_queue.put({
                "query": query,
                "values": values
            })

        except Exception as e:

            print(f"[DB LOGGER] Failed to enqueue trade exit: {e}")


db_logger = DBLogger()
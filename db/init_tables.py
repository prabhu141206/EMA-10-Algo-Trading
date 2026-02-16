from db.connection import create_connection

def init_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,

            symbol TEXT,
            strategy_name TEXT,

            direction TEXT,
            index_price REAL,

            entry_price REAL,
            entry_time TIMESTAMP,

            sl_price REAL,
            target_price REAL,

            exit_price REAL,
            exit_time TIMESTAMP,
            exit_reason TEXT,

            pnl REAL,

            lot_size INTEGER,
            capital_used REAL
        );
    """)

    

    conn.commit()
    cursor.close()
    conn.close()
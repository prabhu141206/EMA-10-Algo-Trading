from db.connection import create_connection

def init_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trade_events (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP,
        event_type VARCHAR(50),
        direction VARCHAR(10),
        price FLOAT,
        trigger_price FLOAT,
        candle_time BIGINT,
        note TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS paper_trades (
        id SERIAL PRIMARY KEY,
        entry_time TIMESTAMP,
        direction VARCHAR(10),
        entry_price FLOAT,
        sl_price FLOAT,
        target_price FLOAT,
        exit_time TIMESTAMP,
        exit_price FLOAT,
        pnl FLOAT
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()
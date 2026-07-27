from psycopg2.pool import SimpleConnectionPool
import os
import time

pool = None


def init_pool():
    global pool

    if pool:
        return

    for _ in range(5):
        try:
            pool = SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                port=os.getenv("DB_PORT")
            )

            print("[DB] Pool created")
            return

        except Exception as e:
            print(f"[DB] Waiting for DB... {e}")
            time.sleep(2)

    raise RuntimeError("Failed to create DB pool")


def get_conn():
    init_pool()
    return pool.getconn()


def release_conn(conn):
    if conn:
        pool.putconn(conn)


def close_pool():
    global pool

    if pool is None:
        return

    print("[DB] Closing connection pool...")
    pool.closeall()
    pool = None
    print("[DB] Connection pool closed.")
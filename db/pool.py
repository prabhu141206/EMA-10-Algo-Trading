from psycopg2.pool import SimpleConnectionPool
import os
import time

pool = None

def init_pool():
    global pool

    if pool:
        return

    DATABASE_URL = os.getenv("DATABASE_URL")

    # retry logic (VERY IMPORTANT for Railway)
    for _ in range(10):
        try:
            pool = SimpleConnectionPool(
                1,
                5,
                dsn=DATABASE_URL
            )
            print("[DB] Pool created")
            return
        except Exception as e:
            print("[DB] Waiting for DB...", e)
            time.sleep(3)

    raise RuntimeError("DB connection failed after retries")


def get_conn():
    init_pool()
    return pool.getconn()


def release_conn(conn):
    pool.putconn(conn)
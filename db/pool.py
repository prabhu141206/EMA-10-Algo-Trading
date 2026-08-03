from psycopg2.pool import SimpleConnectionPool
from config.settings import DATABASE_URL, DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT
import os
import time

pool = None


def init_pool():
    global pool

    if pool:
        return

    for _ in range(5):
        try:
            if DATABASE_URL:

                print("[DB] Using Server PostgreSQL")

                pool = SimpleConnectionPool(
                    1,
                    5,
                    dsn=DATABASE_URL
                )

            else:

                print("[DB] Using Local PostgreSQL")

                pool = SimpleConnectionPool(
                    1,
                    5,
                    host=DB_HOST,
                    database=DB_NAME,
                    user=DB_USER,
                    password=DB_PASS,
                    port=DB_PORT
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

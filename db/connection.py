#____________________________Single responsibility: create DB connection.__________________________________


import psycopg2
import time
from config.settings import DATABASE_URL


def create_connection():
    for attempt in range(5):  # retry 5 times
        try:
            conn = psycopg2.connect(DATABASE_URL)
            print("[DB] Connected")
            return conn

        except psycopg2.OperationalError:
            print(f"[DB] Not ready... retry {attempt + 1}")
            time.sleep(2)

    raise Exception("Database not available after retries")

'''

        use for local system 
def create_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT")
    )
 '''
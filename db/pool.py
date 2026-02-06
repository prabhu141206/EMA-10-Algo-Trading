'''

    Purpose: reuse connections instead of creating new ones every time.
    Why it matters: Opening a DB connection per insert is slow and dangerous under load.
    
    Pool does:
        Create 3–10 persistent connections
        Give connection when needed
        Take it back after use
        Think: “Connection bank”

'''




from psycopg2.pool import SimpleConnectionPool
from db.connection import create_connection

pool = SimpleConnectionPool(
    1,
    5,
    dsn=create_connection().dsn
)

def get_conn():
    return pool.getconn()

def release_conn(conn):
    pool.putconn(conn)
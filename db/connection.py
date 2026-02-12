#____________________________Single responsibility: create DB connection.__________________________________


import psycopg2
from config.settings import DATABASE_URL

def create_connection():
    return psycopg2.connect(
        DATABASE_URL
    )


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
from config.settings import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT,DATABASE_URL
import psycopg2


def create_connection():

    database_url = DATABASE_URL

    # ==============================================
    # Cloud Database (Railway / Supabase / Neon)
    # ==============================================

    if database_url:

        return psycopg2.connect(database_url)

    # ==============================================
    # Local Database
    # ==============================================

    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
    )
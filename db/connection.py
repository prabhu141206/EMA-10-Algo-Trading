import os
import psycopg2


def create_connection():

    database_url = os.getenv("DATABASE_URL")

    # ==============================================
    # Cloud Database (Railway / Supabase / Neon)
    # ==============================================

    if database_url:

        return psycopg2.connect(database_url)

    # ==============================================
    # Local Database
    # ==============================================

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT"),
    )
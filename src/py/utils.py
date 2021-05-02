import os
import psycopg2

def get_db_connection():
    dbname = os.environ.get('DB_NAME', 'vaccines')
    dbuser = os.environ.get('DB_USER', 'postgres')
    dbpassword = os.environ.get('DB_PASSWORD', 'postgres')
    dbhost = os.environ.get('DB_HOST', 'localhost')
    dbport = os.environ.get('DB_PORT', 5432)

    return psycopg2.connect(
        host = dbhost,
        port = dbport,
        database = dbname,
        user = dbuser,
        password = dbpassword
    )


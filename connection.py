
import psycopg2 as pg

def create_connection():
    try:
        conn = pg.connect(
            host="127.0.0.1",
            database="postgres",
            user="postgres",
            password="585904",
            port="5432"
        )
        print("✅ Database connection successful")
        return conn
    except Exception as e:
        print("❌ Error connecting to database:", e)
        return None


import psycopg2 as pg
from psycopg2.extras import LogicalReplicationConnection

def create_connection():
    try:
        conn = pg.connect(
            host="127.0.0.1",
            database="postgres",
            user="postgres",
            password="585904",
            port="5432",
            connection_factory=LogicalReplicationConnection
        )
        print("✅ Database connection successful")
        return conn
    except Exception as e:
        print("❌ Error connecting to database:", e)
        return None

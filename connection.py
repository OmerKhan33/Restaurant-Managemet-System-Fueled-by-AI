import psycopg2 as pg

conn = pg.connect (
    host="127.0.0.1",
    database="postgres",
    user="postgres",
    password="585904",
    port="5432"
)
cursor = conn.cursor()
cursor.execute("SELECT version();")
record = cursor.fetchone()
print("You are connected to - ", record, "\n")
import psycopg2
import psycopg2 as pg
import psycopg2.extras
from configparser import ConfigParser
import os

def config(filename=r'D:\My Coding\final_project_testing\Byte&Bite_AI_Dining_Revolution\database.ini', section='postgresql'):
    """Parse the configuration file and return database connection parameters"""
    # Get the absolute path to the directory containing this script
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Build the full path to the database.ini file
    filepath = os.path.join(basedir, filename)
    
    parser = ConfigParser()
    parser.read(filepath)
    
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
    
    return db

def get_db_connection():
    """Connect to the PostgreSQL database server and return the connection"""
    try:
        # Read connection parameters
        params = config()
        
        # Connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error connecting to the database: {error}")
        return None

def initialize_database():
    """Create necessary tables if they don't exist"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create orders table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                total_amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                address TEXT,
                phone VARCHAR(20)
            )
        ''')
        
        # Create order_items table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(id),
                item_id INTEGER NOT NULL,
                item_name VARCHAR(100) NOT NULL,
                quantity INTEGER NOT NULL,
                price DECIMAL(10, 2) NOT NULL
            )
        ''')
        
        conn.commit()
        cur.close()
        print("Database tables initialized successfully")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error initializing database: {error}")
    finally:
        if conn is not None:
            conn.close()



def create_connection():
    try:
        conn = pg.connect(
            host="127.0.0.1",
            database="dbms_project",
            user="postgres",
            password="pgadmin4",
            port="5432"
        )
        print("✅ Database connection successful")
        return conn
    except Exception as e:
        print("❌ Error connecting to database:", e)
        return None
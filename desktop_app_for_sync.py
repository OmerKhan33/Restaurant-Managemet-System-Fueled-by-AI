import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from pymongo import MongoClient
from tkinter import messagebox
from admin_orders import *
from admin_users import *
from admin_order_items import *
from admin_checkouts import *
from sync_to_firebase import *
from deleted_data import *
from menu_items import *
from feedbacks import *
from view_order_summary_gui import *


# PostgreSQL connection function (your own)
from connection import create_connection

# Secret key (only known inside this app)
SECRET_KEY = "runtimeterror"  # 🔒 Change this to your own secret key


## Important ====================================================================

# Credentials file
# paste the address of the the txt file like in my case it is as following and remember to use double \\
CREDENTIALS_FILE = r'D:\My Coding\final_project_testing\Byte&Bite_AI_Dining_Revolution\credentials.txt'


## Important ====================================================================


# Function to check credentials
def verify_login(username, password):
    if not os.path.exists(CREDENTIALS_FILE):
        print('ohhh')
        return False
    with open(CREDENTIALS_FILE, 'r') as f:
        lines = f.readlines()
        for line in lines:
            saved_username, saved_password = line.strip().split(',')
            if username == saved_username and password == saved_password:
                return True
    return False

# Function to add new admin
def add_new_admin():
    secret = simpledialog.askstring("Secret Key", "Enter Secret Key:", show='*')
    if secret != SECRET_KEY:
        messagebox.showerror("Error", "Invalid Secret Key!")
        return

    new_username = simpledialog.askstring("New Admin", "Enter new username:")
    new_password = simpledialog.askstring("New Admin", "Enter new password:", show='*')

    if new_username and new_password:
        with open(CREDENTIALS_FILE, 'a') as f:
            f.write(f"{new_username},{new_password}\n")
        messagebox.showinfo("Success", "New admin added successfully!")

# ============================================================================================================
def open_orders():
    orders_window = AdminOrdersScreen()
    orders_window.mainloop()

def open_users():
    win = AdminUsersScreen()
    win.mainloop()

def open_order_items():
    win = AdminOrderItemsScreen()
    win.mainloop()

def open_checkouts():
    win = AdminCheckoutsScreen()
    win.mainloop()

def open_realtime_database_upload_screen():
    launch_realtime_db_app()
    
    
def open_del_screen():
    open_deleted_data_window()

def open_menu_items():
    AdminMenuItemsScreen().mainloop()
    
def open_feedback():
    win = AdminFeedbackScreen()
    win.mainloop()

def open_view_order_summary():
    win = OrderSummaryScreen()
    win.mainloop()



def open_data_view_screen():
    data_view_window = tk.Toplevel()
    data_view_window.title("Data View Panel")
    data_view_window.geometry("800x600")

    # Title
    title_label = tk.Label(data_view_window, text="Data View Panel", font=('Arial', 22, 'bold'), fg='darkgreen')
    title_label.pack(pady=10)

    # Frame for buttons
    button_frame = tk.Frame(data_view_window)
    button_frame.pack(pady=10)

    # View Orders Button
    view_orders_button = tk.Button(button_frame, text="View Orders", font=('Arial', 14), width=20, height=2, bg='purple', fg='white',command=open_orders)
    view_orders_button.pack(pady=10)

    users_button = tk.Button(button_frame, text="View Users", font=('Arial', 14), width=20, height=2, bg='purple', fg='white', command=open_users)
    users_button.pack(pady=10)

    users_button = tk.Button(button_frame, text="View Order Items", font=('Arial', 14), width=20, height=2, bg='purple', fg='white', command=open_order_items)
    users_button.pack(pady=10)

    users_button = tk.Button(button_frame, text="View Checkouts", font=('Arial', 14), width=20, height=2, bg='purple', fg='white', command=open_checkouts)
    users_button.pack(pady=10)

    menu_items_button = tk.Button(button_frame, text="View Menu Items", font=('Arial', 14), width=20, height=2, bg='purple', fg='white', command=open_menu_items)
    menu_items_button.pack(pady=10)

    feedback_button = tk.Button(button_frame, text="View Feedback", font=('Arial', 14), width=20, height=2, bg='purple', fg='white', command=open_feedback)
    feedback_button.pack(pady=10)

    feedback_button = tk.Button(button_frame, text="View a View", font=('Arial', 14), width=20, height=2, bg='purple', fg='white', command=open_view_order_summary)
    feedback_button.pack(pady=10)



    # Back Button
    def go_back_to_main():
        data_view_window.destroy()

    back_button = tk.Button(data_view_window, text="Back to Main Screen", command=go_back_to_main, font=('Arial', 12), width=20, bg='gray', fg='white')
    back_button.pack(pady=30)



#=====================================================================================================================

def sync_order_items_to_mongodb():
    try:
        conn = create_connection()
        if not conn:
            messagebox.showerror("Error", "PostgreSQL connection failed.")
            return
        cursor = conn.cursor()

        mongo_client = MongoClient('mongodb://localhost:27017/')
        mongo_db = mongo_client['dbms_proj']
        mongo_order_items_collection = mongo_db['order_items']

        cursor.execute("SELECT id, order_id,item_name, quantity FROM order_items")
        order_items = cursor.fetchall()

        mongo_order_items_collection.delete_many({})

        for item in order_items:
            order_item_doc = {
                'id': item[0],
                'order_id': item[1],
                'item_name': item[2],
                'quantity': int(item[3])
            }
            mongo_order_items_collection.insert_one(order_item_doc)

        cursor.close()
        conn.close()
        mongo_client.close()

        messagebox.showinfo("Success", "✅ Order Items synced from PostgreSQL to MongoDB!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def sync_order_items_to_postgresql():
    try:
        conn = create_connection()
        if not conn:
            messagebox.showerror("Error", "PostgreSQL connection failed.")
            return
        cursor = conn.cursor()

        mongo_client = MongoClient('mongodb://localhost:27017/')
        mongo_db = mongo_client['dbms_proj']
        mongo_order_items_collection = mongo_db['order_items']

        mongo_order_items = mongo_order_items_collection.find()

        cursor.execute("TRUNCATE TABLE order_items CASCADE")
        cursor.execute("delete from del_order_items")

        conn.commit()

        for item in mongo_order_items:
            cursor.execute(
                "INSERT INTO order_items (id , order_id , item_name , quantity) VALUES (%s, %s, %s,%s)",
                (item['id'], item['order_id'], item['item_name'],item['quantity'])
            )
        conn.commit()

        cursor.close()
        conn.close()
        mongo_client.close()

        messagebox.showinfo("Success", "✅ Order Items synced from MongoDB to PostgreSQL!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def sync_checkouts_to_mongodb():
    try:
        conn = create_connection()
        if not conn:
            messagebox.showerror("Error", "PostgreSQL connection failed.")
            return
        cursor = conn.cursor()

        mongo_client = MongoClient('mongodb://localhost:27017/')
        mongo_db = mongo_client['dbms_proj']
        mongo_checkouts_collection = mongo_db['checkouts']

        cursor.execute("SELECT id ,customer_name, order_id, total_amount FROM checkouts")
        checkouts = cursor.fetchall()

        mongo_checkouts_collection.delete_many({})

        for checkout in checkouts:
            checkout_doc = {
                'id': checkout[0],
                'customer_name': checkout[1],
                'order_id': checkout[2],
                'total_amount': float(checkout[3])
            }
            mongo_checkouts_collection.insert_one(checkout_doc)

        cursor.close()
        conn.close()
        mongo_client.close()

        messagebox.showinfo("Success", "✅ Checkouts synced from PostgreSQL to MongoDB!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


import psycopg2
from pymongo import MongoClient

def sync_postgres_to_mongo():
    # PostgreSQL connection
    pg_conn = psycopg2.connect(
        dbname='dbms_project',
        user='postgres',
        password='pgadmin4',
        host='127.0.0.1',
        port='5432'
    )
    pg_cursor = pg_conn.cursor()

    # MongoDB connection
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["dbms_proj"]
    mongo_collection = mongo_db["menu_items"]

    # Clear existing MongoDB data (optional, for full sync)
    mongo_collection.delete_many({})

    # Fetch data from PostgreSQL
    pg_cursor.execute("SELECT id, name, description, price, image, category FROM menu_items")
    rows = pg_cursor.fetchall()

    # Convert and insert into MongoDB
    for row in rows:
        document = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": float(row[3]),
            "image": row[4],
            "category": row[5]
        }
        mongo_collection.insert_one(document)

    # Close connections
    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()

    print("✅ PostgreSQL 'menu_items' synced to MongoDB 'menu_items' collection successfully.")
    messagebox.showinfo('Done','Successfull')


import psycopg2
from pymongo import MongoClient

def sync_mongo_to_postgres():
    # PostgreSQL connection
    pg_conn = psycopg2.connect(
        dbname='dbms_project',
        user='postgres',
        password='pgadmin4',
        host='127.0.0.1',
        port='5432'
    )
    pg_cursor = pg_conn.cursor()

    # MongoDB connection
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["dbms_proj"]
    mongo_collection = mongo_db["menu_items"]

    # Optional: Clear existing PostgreSQL data (for full sync)
    pg_cursor.execute("TRUNCATE TABLE menu_items CASCADE")
    pg_cursor.execute("delete from del_menu_items")

    # Fetch data from MongoDB
    mongo_docs = mongo_collection.find()

    # Insert into PostgreSQL
    for doc in mongo_docs:
        pg_cursor.execute("""
            INSERT INTO menu_items (id, name, description, price, image, category)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                price = EXCLUDED.price,
                image = EXCLUDED.image,
                category = EXCLUDED.category
        """, (
            doc.get("id"),
            doc.get("name"),
            doc.get("description"),
            float(doc.get("price")),
            doc.get("image"),
            doc.get("category")
        ))

    # Commit changes and close connections
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()

    print("✅ MongoDB 'menu_items' synced to PostgreSQL 'menu_items' table successfully.")
    messagebox.showinfo('Done','Successfull')




def sync_checkouts_to_postgresql():
    try:
        conn = create_connection()
        if not conn:
            messagebox.showerror("Error", "PostgreSQL connection failed.")
            return
        cursor = conn.cursor()

        mongo_client = MongoClient('mongodb://localhost:27017/')
        mongo_db = mongo_client['dbms_proj']
        mongo_checkouts_collection = mongo_db['checkouts']

        mongo_checkouts = mongo_checkouts_collection.find()

        cursor.execute("TRUNCATE TABLE checkouts CASCADE")
        cursor.execute("delete from del_checkouts")
        conn.commit()

        for checkout in mongo_checkouts:
            cursor.execute(
                "INSERT INTO checkouts (id, customer_name, order_id, total_amount) VALUES (%s, %s, %s,%s)",
                (checkout['id'],checkout['customer_name'], checkout['order_id'], checkout['total_amount'])
            )
        conn.commit()

        cursor.close()
        conn.close()
        mongo_client.close()

        messagebox.showinfo("Success", "✅ Checkouts synced from MongoDB to PostgreSQL!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


    
def sync_orders_to_postgresql():
    try:
        # Connect to PostgreSQL
        conn = create_connection()
        if not conn:
            messagebox.showerror("Error", "PostgreSQL connection failed.")
            return
        cursor = conn.cursor()

        # Connect to MongoDB
        mongo_client = MongoClient('mongodb://localhost:27017/')
        mongo_db = mongo_client['dbms_proj']
        mongo_orders_collection = mongo_db['orders']

        # Fetch all orders from MongoDB
        mongo_orders = mongo_orders_collection.find()

        # Optional: Clear existing PostgreSQL orders table (to avoid duplicates)
        cursor.execute("TRUNCATE TABLE orders CASCADE")
        cursor.execute("delete from del_orders cascade")

        conn.commit()

        # Insert into PostgreSQL
        for order in mongo_orders:
            cursor.execute(
                "INSERT INTO orders (id, summary, item_names, quantities,order_time) VALUES (%s, %s, %s, %s,%s)",
                (order['order_id'], order['summary'], order['item_names'], order['quantities'],order['order_time'])
            )
        conn.commit()

        cursor.close()
        conn.close()
        mongo_client.close()

        messagebox.showinfo("Success", "✅ Orders synced from MongoDB to PostgreSQL successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def sync_users_to_postgresql():
    try:
        # Connect to PostgreSQL
        conn = create_connection()
        if not conn:
            messagebox.showerror("Error", "PostgreSQL connection failed.")
            return
        cursor = conn.cursor()

        # Connect to MongoDB
        mongo_client = MongoClient('mongodb://localhost:27017/')
        mongo_db = mongo_client['dbms_proj']
        mongo_users_collection = mongo_db['users']

        # Fetch all users from MongoDB
        mongo_users = mongo_users_collection.find()

        # Optional: Clear existing PostgreSQL users table (to avoid duplicates)
        cursor.execute("truncate table users cascade")
        cursor.execute("delete from del_users")
        conn.commit()

        # Insert into PostgreSQL
        for user in mongo_users:
            cursor.execute(
                "INSERT INTO users (id, username, email, password_hash) VALUES (%s, %s, %s, %s)",
                (user['user_id'], user['username'], user['email'], user['password_hash'])
            )
        conn.commit()

        cursor.close()
        conn.close()
        mongo_client.close()

        messagebox.showinfo("Success", "✅ Users synced from MongoDB to PostgreSQL successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def sync_users():
    try:
        # Connect to PostgreSQL
        conn = create_connection()
        if not conn:
            messagebox.showerror("Error", "PostgreSQL connection failed.")
            return

        cursor = conn.cursor()

        # Fetch all users
        cursor.execute("SELECT id, username, email, password_hash FROM users")
        users = cursor.fetchall()

        # Connect to MongoDB
        mongo_client = MongoClient('mongodb://localhost:27017/')
        mongo_db = mongo_client['dbms_proj']
        mongo_users_collection = mongo_db['users']

        # Clear MongoDB collection first (to avoid duplicates)
        mongo_users_collection.delete_many({})

        # Insert fetched users into MongoDB
        for user in users:
            user_doc = {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'password_hash': user[3]
            }
            mongo_users_collection.insert_one(user_doc)

        cursor.close()
        conn.close()
        mongo_client.close()

        messagebox.showinfo("Success", "✅ Users synced to MongoDB successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def sync_orders():
    try:
        # Connect to PostgreSQL
        conn = create_connection()
        if not conn:
            messagebox.showerror("Error", "PostgreSQL connection failed.")
            return

        cursor = conn.cursor()

        # Fetch all orders
        cursor.execute("SELECT id, summary, item_names, quantities, order_time FROM orders")
        orders = cursor.fetchall()

        # Connect to MongoDB
        mongo_client = MongoClient('mongodb://localhost:27017/')
        mongo_db = mongo_client['dbms_proj']
        mongo_orders_collection = mongo_db['orders']

        # Clear MongoDB collection first (to avoid duplicates)
        mongo_orders_collection.delete_many({})

        # Insert fetched orders into MongoDB
        for order in orders:
            order_doc = {
                'order_id': order[0],
                'summary': order[1],
                'item_names': order[2],
                'quantities': order[3],
                'order_time': order[4]
            }
            mongo_orders_collection.insert_one(order_doc)

        cursor.close()
        conn.close()
        mongo_client.close()

        messagebox.showinfo("Success", "✅ Orders synced to MongoDB successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")



import psycopg2
from pymongo import MongoClient
import base64

def sync_feedbacks_postgres_to_mongo():
    # PostgreSQL connection
    pg_conn = psycopg2.connect(
        dbname='dbms_project',
        user='postgres',
        password='pgadmin4',
        host='127.0.0.1',
        port='5432'
    )
    pg_cursor = pg_conn.cursor()

    # MongoDB connection
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["dbms_proj"]
    mongo_collection = mongo_db["feedbacks"]

    # Clear existing MongoDB data
    mongo_collection.delete_many({})

    # Fetch data from PostgreSQL
    pg_cursor.execute("SELECT id, user_name, order_id, order_name, description, bad_order_image FROM feedbacks")
    rows = pg_cursor.fetchall()

    for row in rows:
        # Convert binary image to base64 string (safe for MongoDB)
        image_data = base64.b64encode(row[5]).decode('utf-8') if row[5] else None

        document = {
            "id": row[0],
            "user_name": row[1],
            "order_id": row[2],
            "order_name": row[3],
            "description": row[4],
            "bad_order_image": image_data
        }
        mongo_collection.insert_one(document)

    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()

    print("✅ PostgreSQL 'feedbacks' table synced to MongoDB 'feedbacks' collection successfully.")
    messagebox.showinfo('Done','Successfull')


def sync_feedbacks_mongo_to_postgres():
    # PostgreSQL connection
    pg_conn = psycopg2.connect(
        dbname='dbms_project',
        user='postgres',
        password='pgadmin4',
        host='127.0.0.1',
        port='5432'
    )
    pg_cursor = pg_conn.cursor()

    # MongoDB connection
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["dbms_proj"]
    mongo_collection = mongo_db["feedbacks"]

    # Optional: Clear existing PostgreSQL data
    pg_cursor.execute("truncate table feedbacks cascade")
    pg_cursor.execute("delete from del_feedbacks")

    for doc in mongo_collection.find():
        # Decode base64 image back to binary
        image_data = base64.b64decode(doc.get("bad_order_image")) if doc.get("bad_order_image") else None

        pg_cursor.execute("""
            INSERT INTO feedbacks (id, user_name, order_id, order_name, description, bad_order_image)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                user_name = EXCLUDED.user_name,
                order_id = EXCLUDED.order_id,
                order_name = EXCLUDED.order_name,
                description = EXCLUDED.description,
                bad_order_image = EXCLUDED.bad_order_image
        """, (
            doc.get("id"),
            doc.get("user_name"),
            doc.get("order_id"),
            doc.get("order_name"),
            doc.get("description"),
            image_data
        ))

    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()

    print("✅ MongoDB 'feedbacks' collection synced to PostgreSQL 'feedbacks' table successfully.")
    messagebox.showinfo('Done', 'Successfull')

# After successful login, show the main app
def open_main_screen():
    login_window.destroy()

    main_app = tk.Tk()
    main_app.title("Order Synchronization Panel")
    main_app.geometry("1100x750")

    # --------- Canvas & Scrollbar Setup ---------
    main_canvas = tk.Canvas(main_app)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(main_app, orient=tk.VERTICAL, command=main_canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    main_canvas.configure(yscrollcommand=scrollbar.set)
    main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

    scrollable_frame = tk.Frame(main_canvas)
    main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    # ------------------------------------------------

    # Title Label
    sync_label = tk.Label(scrollable_frame, text="Order Synchronization Panel", font=('Arial', 24, 'bold'), fg='purple')
    sync_label.pack(pady=20)

    # Main frame to hold left and right frames
    main_frame = tk.Frame(scrollable_frame)
    main_frame.pack(pady=20)

    left_frame = tk.Frame(main_frame)
    left_frame.pack(side='left', padx=50)

    right_frame = tk.Frame(main_frame)
    right_frame.pack(side='right', padx=50)

    # PostgreSQL ➔ MongoDB
    tk.Button(left_frame, text="Sync Orders from PostgreSQL to MongoDB", command=sync_orders, font=('Arial', 14), width=38, height=2, bg='blue', fg='white').pack(pady=10)
    tk.Button(left_frame, text="Sync Users from PostgreSQL to MongoDB", command=sync_users, font=('Arial', 14), width=38, height=2, bg='blue', fg='white').pack(pady=10)
    tk.Button(left_frame, text="Sync Order Items from PostgreSQL to MongoDB", command=sync_order_items_to_mongodb, font=('Arial', 14), width=38, height=2, bg='blue', fg='white').pack(pady=10)
    tk.Button(left_frame, text="Sync Checkouts from PostgreSQL to MongoDB", command=sync_checkouts_to_mongodb, font=('Arial', 14), width=38, height=2, bg='blue', fg='white').pack(pady=10)
    tk.Button(left_frame, text="Sync Menu Items from PostgreSQL to MongoDB", command=sync_postgres_to_mongo, font=('Arial', 14), width=38, height=2, bg='blue', fg='white').pack(pady=10)
    tk.Button(left_frame, text="Sync Feedbacks from PostgreSQL to MongoDB", command=sync_feedbacks_postgres_to_mongo, font=('Arial', 14), width=38, height=2, bg='blue', fg='white').pack(pady=10)

    # MongoDB ➔ PostgreSQL
    tk.Button(right_frame, text="Sync Orders from MongoDB to PostgreSQL", command=sync_orders_to_postgresql, font=('Arial', 14), width=38, height=2, bg='red', fg='white').pack(pady=10)
    tk.Button(right_frame, text="Sync Users from MongoDB to PostgreSQL", command=sync_users_to_postgresql, font=('Arial', 14), width=38, height=2, bg='red', fg='white').pack(pady=10)
    tk.Button(right_frame, text="Sync Order Items from MongoDB to PostgreSQL", command=sync_order_items_to_postgresql, font=('Arial', 14), width=38, height=2, bg='red', fg='white').pack(pady=10)
    tk.Button(right_frame, text="Sync Checkouts from MongoDB to PostgreSQL", command=sync_checkouts_to_postgresql, font=('Arial', 14), width=38, height=2, bg='red', fg='white').pack(pady=10)
    tk.Button(right_frame, text="Sync Menu Items from MongoDB to PostgreSQL", command=sync_mongo_to_postgres, font=('Arial', 14), width=38, height=2, bg='red', fg='white').pack(pady=10)
    tk.Button(right_frame, text="Sync Feedbacks from MongoDB to PostgreSQL", command=sync_feedbacks_mongo_to_postgres, font=('Arial', 14), width=38, height=2, bg='red', fg='white').pack(pady=10)

    # Admin Control Section
    admin_button_frame = tk.Frame(scrollable_frame)
    admin_button_frame.pack(pady=30)

    row1 = tk.Frame(admin_button_frame)
    row1.pack(pady=10)

    tk.Button(row1, text="Add New Admin", command=add_new_admin, font=('Arial', 14), width=25, height=2, bg='purple', fg='white').pack(side=tk.LEFT, padx=20)
    tk.Button(row1, text="View Data", command=open_data_view_screen, font=('Arial', 14), width=25, height=2, bg='green', fg='white').pack(side=tk.LEFT, padx=20)

    row2 = tk.Frame(admin_button_frame)
    row2.pack(pady=10)

    tk.Button(row2, text="Upload & Sync Data to Realtime DB", command=open_realtime_database_upload_screen, font=('Arial', 14), width=40, height=2, bg='green', fg='white').pack(side=tk.LEFT, padx=20)
    tk.Button(row2, text="Open Deleted Data Screen", command=open_del_screen, font=('Arial', 14), width=35, height=2, bg='green', fg='white').pack(side=tk.LEFT, padx=20)

    main_app.mainloop()






# Login window
def login():
    username = username_entry.get()
    password = password_entry.get()

    if verify_login(username, password):
        open_main_screen()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# --- MAIN SCREEN ---
login_window = tk.Tk()
login_window.title("Admin Login")
login_window.geometry("350x250")

tk.Label(login_window, text="Username:", font=('Arial', 12)).pack(pady=5)
username_entry = tk.Entry(login_window, font=('Arial', 12))
username_entry.pack(pady=5)

tk.Label(login_window, text="Password:", font=('Arial', 12)).pack(pady=5)
password_entry = tk.Entry(login_window, font=('Arial', 12), show="*")
password_entry.pack(pady=5)

login_button = tk.Button(login_window, text="Login", command=login, font=('Arial', 12), bg='black', fg='white')
login_button.pack(pady=20)

login_window.mainloop()

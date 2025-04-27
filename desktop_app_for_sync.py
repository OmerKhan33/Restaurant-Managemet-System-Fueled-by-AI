import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from pymongo import MongoClient
from tkinter import messagebox

# PostgreSQL connection function (your own)
from connection import create_connection

# Secret key (only known inside this app)
SECRET_KEY = "runtimeterror"  # 🔒 Change this to your own secret key


## Important ====================================================================

# Credentials file
# paste the address of the the txt file like in my case it is as following and remember to use double \\
CREDENTIALS_FILE = 'D:\\My Coding\\Byte&Bite_AI_Dining_Revolution\\credentials.txt'


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

        cursor.execute("SELECT item_id, order_id,item_name, quantity FROM order_items")
        order_items = cursor.fetchall()

        mongo_order_items_collection.delete_many({})

        for item in order_items:
            order_item_doc = {
                'item_id': item[0],
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

        cursor.execute("TRUNCATE TABLE order_items RESTART IDENTITY CASCADE")
        conn.commit()

        for item in mongo_order_items:
            cursor.execute(
                "INSERT INTO order_items (item_id , order_id , item_name , quantity) VALUES (%s, %s, %s,%s)",
                (item['item_id'], item['order_id'], item['item_name'],item['quantity'])
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

        cursor.execute("TRUNCATE TABLE checkouts RESTART IDENTITY CASCADE")
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
        cursor.execute("TRUNCATE TABLE orders RESTART IDENTITY CASCADE")

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
        cursor.execute("DELETE FROM users")
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


# After successful login, show the main app
def open_main_screen():
    login_window.destroy()

    main_app = tk.Tk()
    main_app.title("Order Synchronization Panel")
    main_app.geometry("1100x750")  # Wider window for full text buttons

    # Title Label
    sync_label = tk.Label(main_app, text="Order Synchronization Panel", font=('Arial', 24, 'bold'), fg='purple')
    sync_label.pack(pady=20)

    # Main frame to hold left and right frames
    main_frame = tk.Frame(main_app)
    main_frame.pack(pady=20)

    # Left Frame (PostgreSQL to MongoDB)
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side='left', padx=50)

    # Right Frame (MongoDB to PostgreSQL)
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side='right', padx=50)

    # ----- Left Side: PostgreSQL ➔ MongoDB (Blue Buttons) -----

    sync_orders_button = tk.Button(left_frame, text="Sync Orders from PostgreSQL to MongoDB", command=sync_orders, font=('Arial', 14), width=38, height=2, bg='blue', fg='white')
    sync_orders_button.pack(pady=10)

    sync_users_button = tk.Button(left_frame, text="Sync Users from PostgreSQL to MongoDB", command=sync_users, font=('Arial', 14), width=38, height=2, bg='blue', fg='white')
    sync_users_button.pack(pady=10)

    sync_order_items_mongo_button = tk.Button(left_frame, text="Sync Order Items from PostgreSQL to MongoDB", command=sync_order_items_to_mongodb, font=('Arial', 14), width=38, height=2, bg='blue', fg='white')
    sync_order_items_mongo_button.pack(pady=10)

    sync_checkouts_mongo_button = tk.Button(left_frame, text="Sync Checkouts from PostgreSQL to MongoDB", command=sync_checkouts_to_mongodb, font=('Arial', 14), width=38, height=2, bg='blue', fg='white')
    sync_checkouts_mongo_button.pack(pady=10)

    # ----- Right Side: MongoDB ➔ PostgreSQL (Red Buttons) -----

    sync_orders_pg_button = tk.Button(right_frame, text="Sync Orders from MongoDB to PostgreSQL", command=sync_orders_to_postgresql, font=('Arial', 14), width=38, height=2, bg='red', fg='white')
    sync_orders_pg_button.pack(pady=10)

    sync_users_pg_button = tk.Button(right_frame, text="Sync Users from MongoDB to PostgreSQL", command=sync_users_to_postgresql, font=('Arial', 14), width=38, height=2, bg='red', fg='white')
    sync_users_pg_button.pack(pady=10)

    sync_order_items_pg_button = tk.Button(right_frame, text="Sync Order Items from MongoDB to PostgreSQL", command=sync_order_items_to_postgresql, font=('Arial', 14), width=38, height=2, bg='red', fg='white')
    sync_order_items_pg_button.pack(pady=10)

    sync_checkouts_pg_button = tk.Button(right_frame, text="Sync Checkouts from MongoDB to PostgreSQL", command=sync_checkouts_to_postgresql, font=('Arial', 14), width=38, height=2, bg='red', fg='white')
    sync_checkouts_pg_button.pack(pady=10)

    # ----- Admin Control (at Bottom) -----

    add_admin_button = tk.Button(main_app, text="Add New Admin", command=add_new_admin, font=('Arial', 14), width=20, height=2, bg='purple', fg='white')
    add_admin_button.pack(pady=30)

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

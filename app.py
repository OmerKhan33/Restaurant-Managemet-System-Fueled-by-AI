from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from connection import create_connection
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash/session management

# -------------------- ROUTES -------------------- #
# MongoDB connection
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['dbms_proj']
mongo_orders_collection = mongo_db['orders']

@app.route('/sync_orders')
def sync_orders():
    conn = create_connection()
    if not conn:
        flash("PostgreSQL connection failed.")
        return redirect(url_for('index'))

    cursor = conn.cursor()

    # Fetch all orders
    cursor.execute("SELECT id, summary, item_names, quantities FROM orders")
    orders = cursor.fetchall()

    # Clear MongoDB collection first (optional, to avoid duplicates)
    mongo_orders_collection.delete_many({})

    # Insert into MongoDB
    for order in orders:
        order_doc = {
            'order_id': order[0],
            'summary': order[1],
            'item_names': order[2],
            'quantities': order[3]
        }
        mongo_orders_collection.insert_one(order_doc)

    cursor.close()
    conn.close()

    flash("✅ Orders synced to MongoDB successfully!")
    return redirect(url_for('index'))
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/insights')
def insights():
    if 'user' not in session:
        flash("🔒 You must be logged in to view insights.")
        return redirect(url_for('login'))
    return render_template('insights.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = create_connection()
        if not conn:
            flash("Database connection failed.")
            return redirect(url_for('signup'))

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("📧 Email already registered.")
            cursor.close()
            conn.close()
            return redirect(url_for('signup'))

        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Account created successfully! Please login.")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = create_connection()
        if not conn:
            flash("Database connection failed.")
            return redirect(url_for('login'))

        cursor = conn.cursor()
        cursor.execute("SELECT username, password_hash FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user'] = user[0]
            flash(f"👋 Welcome, {user[0]}!")
            return redirect(url_for('index'))
        else:
            flash("❌ Invalid credentials.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("👋 Logged out successfully.")
    return redirect(url_for('index'))

@app.route('/order_details/<int:order_id>')
def order_details(order_id):
    conn = create_connection()
    if not conn:
        return "Database connection failed", 500

    cursor = conn.cursor()

    # Fetch order info
    cursor.execute("SELECT id, summary, item_names, quantities FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()

    if not order:
        flash("❌ Order not found.")
        return redirect('/order')

    # Fetch items and quantities
    cursor.execute("SELECT item_name, quantity FROM order_items WHERE order_id = %s", (order_id,))
    items = cursor.fetchall()

    # Simple pricing model (can be replaced with actual DB-driven prices)
    prices = {'Burger': 5.99, 'Fries': 2.99, 'Drink': 1.99}
    total = sum(prices[item[0]] * item[1] for item in items)

    cursor.close()
    conn.close()

    return render_template('order_details.html', order_id=order_id, items=items, total=total, customer=session.get('user', 'Guest'))

@app.route('/submit_order', methods=['POST'])
def submit_order():
    conn = create_connection()
    if not conn:
        return "Database connection failed", 500

    cursor = conn.cursor()

    items = ['Burger', 'Fries', 'Drink']
    order_summary_parts = []
    order_items_to_insert = []
    item_names = []
    quantities = []

    for item in items:
        qty_str = request.form.get(item)
        if qty_str and qty_str.isdigit():
            qty = int(qty_str)
            if qty > 0:
                order_summary_parts.append(f"{item} x{qty}")
                order_items_to_insert.append((item, qty))
                item_names.append(item)
                quantities.append(str(qty))

    if not order_items_to_insert:
        flash("❌ You must select at least one item.")
        return redirect('/order')

    summary_string = ", ".join(order_summary_parts)
    item_names_string = ", ".join(item_names)
    quantities_string = ", ".join(quantities)

    cursor.execute(
        "INSERT INTO orders (summary, item_names, quantities) VALUES (%s, %s, %s) RETURNING id",
        (summary_string, item_names_string, quantities_string)
    )
    order_id = cursor.fetchone()[0]

    for item, qty in order_items_to_insert:
        cursor.execute(
            "INSERT INTO order_items (order_id, item_name, quantity) VALUES (%s, %s, %s)",
            (order_id, item, qty)
        )

         # Calculate total (use same pricing logic as order_details route)
    prices = {'Burger': 5.99, 'Fries': 2.99, 'Drink': 1.99}
    total = sum(prices[item] * qty for item, qty in order_items_to_insert)

# Insert into checkouts
    customer_name = session.get('user', 'Guest')
    cursor.execute(
    "INSERT INTO checkouts (customer_name, order_id, total_amount) VALUES (%s, %s, %s)",
    (customer_name, order_id, total)
    )

    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Order placed successfully!")
    return redirect(url_for('order_details', order_id=order_id))



# ------------------------------------------------ #

if __name__ == '__main__':
    app.run(debug=True)

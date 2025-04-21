# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from werkzeug.security import generate_password_hash, check_password_hash

# from flask import Flask, render_template, redirect, url_for, request, session, flash
# from flask_login import LoginManager, login_user, logout_user, login_required, current_user


# app = Flask(__name__)
# app.secret_key = 'supersecretkey'  # Needed for session management

# # Dummy in-memory database (username/email: {info})
# users_db = {}

# # ---------------- ROUTES ---------------- #

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/order')
# def order():
#     return render_template('order.html')

# @app.route('/insights')
# def insights():
#     if 'user' not in session:
#         flash("You must be logged in to view insights.")
#         return redirect(url_for('login'))
#     return render_template('insights.html')

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']

#         if email in users_db:
#             flash('Email already registered.')
#             return redirect(url_for('signup'))

#         hashed_password = generate_password_hash(password)
#         users_db[email] = {'username': username, 'password': hashed_password}
#         flash('Account created successfully! Please login.')
#         return redirect(url_for('login'))
#     return render_template('signup.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         user = users_db.get(email)
#         if user and check_password_hash(user['password'], password):
#             session['user'] = user['username']
#             flash(f"Welcome, {user['username']}!")
#             return redirect(url_for('index'))
#         else:
#             flash("Invalid credentials.")
#             return redirect(url_for('login'))
#     return render_template('login.html')






# # ---------------------------------------- #

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from connection import create_connection

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash/session management

# Dummy in-memory user database
users_db = {}

# -------------------- ROUTES -------------------- #

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/order')
def order():
    return render_template('order.html')

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

    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Order placed successfully!")
    return redirect('/order')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

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

        if email in users_db:
            flash('📧 Email already registered.')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        users_db[email] = {'username': username, 'password': hashed_password}
        flash('✅ Account created! Please login.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_db.get(email)
        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            flash(f"👋 Welcome, {user['username']}!")
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

# ------------------------------------------------ #

if __name__ == '__main__':
    app.run(debug=True)

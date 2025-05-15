from flask import Flask, render_template, redirect, url_for, request, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
from connection import get_db_connection, initialize_database
import os

us =['Guest']

app = Flask(__name__)
app.secret_key = 'byteandbite_secret_key'  # Required for session

# Initialize database tables
initialize_database()



import os
import google.generativeai as genai
from flask import request, jsonify

# Configure Gemini API
genai.configure(api_key="AIzaSyC-p-m0sKZ5z1f5lbkObVOB37L8FqjY8JA")
model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-1219")



from flask import make_response
from reportlab.pdfgen import canvas
from io import BytesIO

@app.route('/receipt/<int:order_id>')
def generate_receipt(order_id):
    conn = get_db_connection()
    if conn is None:
        return "DB connection failed", 500
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cur.fetchone()

        cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
        items = cur.fetchall()
        cur.close()
        conn.close()

        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, "Byte & Bite - Order Receipt")

        p.setFont("Helvetica", 12)
        y = 770
        p.drawString(100, y, f"Order ID: {order['id']}")
        y -= 20
        p.drawString(100, y, f"Items:")
        y -= 20

        for item in items:
            p.drawString(120, y, f"{item['item_name']} x {item['quantity']}")
            y -= 20

        y -= 10
        p.drawString(100, y, f"Summary: {order['summary']}")
        y -= 30
        p.drawString(100, y, "Thank you for ordering with Byte & Bite!")

        p.showPage()
        p.save()
        buffer.seek(0)

        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=receipt_order_{order_id}.pdf'
        return response
    except Exception as e:
        return f"Error generating receipt: {e}", 500


@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    user_input = data.get("message", "")
    
    try:
        custom_prompt = (
    "You are ByteBot, a friendly AI assistant for a restaurant. and  you are working in a restaurant called Byte and Bite.\n"
    "You are knowledgeable about the menu, orders, and general restaurant information.\n"
    "Your task is to assist users with their inquiries and provide helpful responses.\n"
    "You are not allowed to provide any personal information about the restaurant or its employees.\n"
    "You are not allowed to anything else except Food and the process how to Order and if  user asks how to order orsomething related to it gently respose him that currently you are  in orders section simplyselect your fav dish and click on the cart icon on top right and then boom your order is now placed\n"
    "Answer clearly and help users with menu items, orders, and general questions.\n\n"
    f"User: {user_input}"
)

        response = model.generate_content(custom_prompt)

        reply = response.text
    except Exception as e:
        reply = "Sorry, something went wrong."

    return jsonify({"reply": reply})


# Authentication middleware
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Add a debugging route to print all available routes
@app.route('/debug-routes')
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "path": str(rule)
        })
    return jsonify(routes)

# Initialize cart in session if it doesn't exist
@app.before_request
def initialize_session():
    if 'cart' not in session:
        session['cart'] = []

@app.route('/')
def index():
    """Root route that redirects to the main page"""
    return redirect(url_for('layout'))

@app.route('/landing')
def landing():
    """Landing page route (consider deprecating)"""
    return render_template('layout.html')

@app.route('/layout')
def layout():
    """Layout page"""
    items = fetch_menu_items()
    return render_template('layout.html', menu_items=items)




@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Retrieve form data
        user_name = us[-1]
        order_id = request.form['order_id']
        order_name = request.form['order_name']
        description = request.form.get('description', '')
        
        # Handle image upload (if any)
        bad_order_image = request.files.get('bad_order_image')
        bad_order_image_data = None
        if bad_order_image:
            bad_order_image_data = bad_order_image.read()  # Read image as binary data
        
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insert into feedbacks table
            insert_query = """
                INSERT INTO feedbacks (user_name, order_id, order_name, description, bad_order_image)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, (user_name, order_id, order_name, description, bad_order_image_data))
            conn.commit()

            flash("Thank you for your feedback!", "success")
            return redirect(url_for('feedback'))  # Redirect back to feedback page or another page

        except Exception as e:
            conn.rollback()
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for('feedback'))

        finally:
            cursor.close()
            conn.close()

    # Check if the user is logged in
    user = session.get('username')  # Fetch the username from session (it will be None if not logged in)

    return render_template('feedback.html', user=user)


@app.route('/menu')
def menu():
    """Menu page showing all available food items"""
    items = fetch_menu_items()
    return render_template('menu.html', menu_items=items)
def fetch_menu_items(category=None):
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if category and category != 'all':
            cur.execute("SELECT * FROM menu_items WHERE category = %s", (category,))
        else:
            cur.execute("SELECT * FROM menu_items")
        items = cur.fetchall()
        cur.close()
        conn.close()
        return items
    except Exception as e:
        print("Error fetching menu items:", e)
        return []

# Authentication routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))
        
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error', 'error')
            return redirect(url_for('signup'))
        
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Check if username already exists
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cur.fetchone() is not None:
                flash('Username already exists', 'error')
                cur.close()
                conn.close()
                return redirect(url_for('signup'))
            
            # Check if email already exists
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cur.fetchone() is not None:
                flash('Email already exists', 'error')
                cur.close()
                conn.close()
                return redirect(url_for('signup'))
            
            # Store new user with hashed password
            hashed_password = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            conn.close()
            return redirect(url_for('signup'))
    
    return render_template('signup.html')

# Global variable to store the username for checkout

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        us.append(username)
        password = request.form['password']
        
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error', 'error')
            return redirect(url_for('login'))
        
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))

            user = cur.fetchone()
            cur.close()
            conn.close()
            
            if user and check_password_hash(user['password_hash'], password):
                session['username'] = username
                session['user_id'] = user['id']
                flash('Logged in successfully!', 'success')
                return redirect(url_for('menu'))
            else:
                flash('Invalid username or password', 'error')
                
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            conn.close()
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('menu'))

@app.route('/profile')
@login_required
def profile():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'error')
        return redirect(url_for('menu'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s", (session.get('username'),))
        user = cur.fetchone()
        
        # # Get order history
        # cur.execute("""
        #     SELECT o.id, o.total_amount, o.status, o.created_at 
        #     FROM orders o
        #     WHERE o.user_id = %s
        #     ORDER BY o.created_at DESC
        # """, (user['id'],))
        # orders = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('menu.html')
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        conn.close()
        return redirect(url_for('menu'))

# Cart operations
@app.route('/cart/add/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    item = get_menu_item_by_id(item_id)
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    
    cart = session.get('cart', [])
    
    # Check if item already in cart
    for cart_item in cart:
        if cart_item['id'] == item_id:
            cart_item['quantity'] += 1
            session['cart'] = cart
            return jsonify({
                'success': True, 
                'cart': cart,
                'total': sum(item['price'] * item['quantity'] for item in cart),
                'count': sum(item['quantity'] for item in cart)
            })
    
    # Item not in cart, add it
    cart_item = {
        'id': item['id'],
        'name': item['name'],
        'price': float(item['price']),
        'quantity': 1
    }
    cart.append(cart_item)
    session['cart'] = cart
    
    return jsonify({
        'success': True, 
        'cart': cart,
        'total': sum(float(item['price']) * int(item['quantity']) for item in cart),
        'count': sum(int(item['quantity']) for item in cart)
    })

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    cart = session.get('cart', [])
    session['cart'] = [item for item in cart if item['id'] != item_id]
    
    updated_cart = session['cart']
    return jsonify({
        'success': True, 
        'cart': updated_cart,
        'total': sum(item['price'] * item['quantity'] for item in updated_cart),
        'count': sum(item['quantity'] for item in updated_cart)
    })


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'GET':
        if not session.get('user_id'):
            flash('Please log in to checkout', 'error')
            return redirect(url_for('login'))

        cart = session.get('cart', [])
        print("DEBUG - Cart contents in session (GET):", cart)  # 👈 Debug line

        if not cart:
            flash('Your cart is empty', 'error')
            return redirect(url_for('menu'))

        total = sum(item['price'] * item['quantity'] for item in cart)
        return render_template('checkout.html', cart=cart, total=total)

        

    elif request.method == 'POST':
        if not session.get('user_id'):
            return jsonify({'success': False, 'message': 'Please log in to checkout'}), 401

        cart = session.get('cart')
        if not cart:
            return jsonify({'success': False, 'message': 'Your cart is empty'}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Database connection error'}), 500

        try:
            cur = conn.cursor()
            total_amount = sum(item['price'] * item['quantity'] for item in cart)

            # Build order summary (currently placeholder)
            summary_parts = []
            summary = "; ".join(summary_parts) if summary_parts else "No additional info"

            item_names = ', '.join([item['name'] for item in cart])
            quantities = ', '.join([str(item['quantity']) for item in cart])

            # Insert into orders table
            cur.execute("""
                INSERT INTO orders (summary, item_names, quantities)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (summary, item_names, quantities))
            order_id = cur.fetchone()[0]

            # Insert each item into order_items
            for item in cart:
                cur.execute("""
                    INSERT INTO order_items (order_id, item_name, quantity)
                    VALUES (%s, %s, %s)
                """, (order_id, item['name'], item['quantity']))

            # Get name from the form directly
            username = us[-1]

            # Insert into checkouts
            cur.execute("""
                INSERT INTO checkouts (customer_name, order_id, total_amount)
                VALUES (%s, %s, %s)
            """, (username, order_id, total_amount))

            conn.commit()
            cur.close()
            conn.close()

            session['cart'] = []

            # JSON response for frontend (to generate PDF)
            return jsonify({
                'success': True,
                'order_id': order_id,
                'item_names': item_names
            })

        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500




@app.route('/filter/<category>')
def filter_menu(category):
    items = fetch_menu_items(category)
    items_list = [dict(item) for item in items]
    return jsonify({'items': items_list})
def get_menu_item_by_id(item_id):
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM menu_items WHERE id = %s", (item_id,))
        item = cur.fetchone()
        cur.close()
        conn.close()
        return item
    except Exception as e:
        print("Error fetching menu item:", e)
        return None

@app.route('/order/<int:order_id>')
@login_required
def order(order_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'error')
        return redirect(url_for('profile'))

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get order details (no user_id filtering possible)
        cur.execute("""
            SELECT * FROM orders
            WHERE id = %s
        """, (order_id,))
        order = cur.fetchone()

        if not order:
            flash('Order not found', 'error')
            cur.close()
            conn.close()
            return redirect(url_for('profile'))

        # Get order items
        cur.execute("""
            SELECT * FROM order_items
            WHERE order_id = %s
        """, (order_id,))
        items = cur.fetchall()

        cur.close()
        conn.close()

        return render_template('order.html', order=order, items=items)

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        conn.close()
        return redirect(url_for('profile'))


# Add script to find template files that might be causing the BuildError
def scan_templates_for_home_references():
    """Function to scan template files for references to 'home'"""
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    results = []
    
    if not os.path.exists(template_dir):
        return {"error": f"Template directory not found at {template_dir}"}
    
    for root, _, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Look for url_for('menu') patterns
                        if "url_for('menu')" in content or 'url_for("menu")' in content:
                            results.append({
                                "file": os.path.relpath(filepath, template_dir),
                                "contains_menu_reference": True
                            })
                except Exception as e:
                    results.append({
                        "file": os.path.relpath(filepath, template_dir),
                        "error": str(e)
                    })
    
    return results

from flask import Flask, render_template, request, send_file
import psycopg2
import io
from reportlab.pdfgen import canvas
from datetime import datetime


@app.route('/debug-templates')
def debug_templates():
    """Route to scan templates for references to 'home'"""
    results = scan_templates_for_home_references()
    return jsonify(results)


@app.route('/usercheckouts')
def user_checkouts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, item_names, quantities FROM orders ORDER BY id DESC limit 1")
    orders = cur.fetchall()
    customer_name = us[-1]
    return render_template('usercheckouts.html', orders=orders, customer_name=customer_name)

from flask import send_file
import io
from reportlab.pdfgen import canvas
from datetime import datetime

@app.route('/download_receipt')
def download_receipt():
    conn = get_db_connection()
    cur = conn.cursor()

    # Get the latest order
    cur.execute("SELECT id, item_names, quantities FROM orders ORDER BY id DESC LIMIT 1")
    order = cur.fetchone()

    if not order:
        return "No orders found", 404

    order_id, item_names_str, quantities_str = order
    items = item_names_str.split(', ')
    quantities = list(map(int, quantities_str.split(', ')))

    # Fetch prices using JOIN
    format_items = tuple(items) if len(items) > 1 else f"('{items[0]}')"  # Prevent SQL error for 1 item
    cur.execute(f"""
        SELECT name, price
        FROM menu_items
        WHERE name IN {format_items}
    """)
    item_price_map = {name: float(price) for name, price in cur.fetchall()}
    conn.close()

    customer_name = us[-1]

    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 800, "Byte & Bite Receipt")

    p.setFont("Helvetica", 12)
    p.drawString(50, 780, f"Customer: {customer_name}")
    p.drawString(50, 765, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = 730
    p.drawString(50, y, f"Order ID: {order_id}")
    y -= 20

    # Table Headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(60, y, "Item")
    p.drawString(240, y, "Quantity")
    p.drawString(360, y, "Price")
    y -= 15
    p.setFont("Helvetica", 12)

    total_price = 0.0

    for item, qty in zip(items, quantities):
        price = item_price_map.get(item, 0.0)
        item_total = price * qty
        total_price += item_total

        p.drawString(60, y, item)
        p.drawString(240, y, str(qty))
        p.drawString(360, y, f"${price:.2f}")
        y -= 20

        if y < 100:
            p.showPage()
            y = 800

    # Draw total
    y -= 10
    p.setFont("Helvetica-Bold", 12)
    p.drawString(240, y, "Total:")
    p.drawString(360, y, f"${total_price:.2f}")

    p.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="receipt.pdf", mimetype='application/pdf')





@app.route('/checkout_page')
def checkout_page():
    return redirect(url_for('checkout'))


if __name__ == '__main__':
    app.run(debug=True)

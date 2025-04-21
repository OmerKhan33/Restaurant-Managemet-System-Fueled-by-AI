
from flask import Flask, render_template, request, redirect,flash
from connection import create_connection

app = Flask(__name__)

app.secret_key = '123'  # you can use any random string here

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

    # Step 1: Collect items and quantities
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

    # Step 2: Insert into orders with summary, item_names, and quantities
    summary_string = ", ".join(order_summary_parts)
    item_names_string = ", ".join(item_names)
    quantities_string = ", ".join(quantities)

    cursor.execute(
        "INSERT INTO orders (summary, item_names, quantities) VALUES (%s, %s, %s) RETURNING id",
        (summary_string, item_names_string, quantities_string)
    )
    order_id = cursor.fetchone()[0]

    # Step 3: Insert each item into order_items
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
    return render_template('insights.html')

if __name__ == '__main__':
    app.run(debug=True)

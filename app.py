from flask import Flask, render_template, request

app = Flask(__name__)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Kiosk Ordering route
@app.route('/order')
def order():
    return render_template('order.html')

# Chatbot route
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# Insights route (Admin dashboard)
@app.route('/insights')
def insights():
    return render_template('insights.html')

if __name__ == '__main__':
    app.run(debug=True)

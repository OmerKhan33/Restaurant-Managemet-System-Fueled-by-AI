from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session management

# Dummy in-memory database (username/email: {info})
users_db = {}

# ---------------- ROUTES ---------------- #

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/insights')
def insights():
    if 'user' not in session:
        flash("You must be logged in to view insights.")
        return redirect(url_for('login'))
    return render_template('insights.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if email in users_db:
            flash('Email already registered.')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        users_db[email] = {'username': username, 'password': hashed_password}
        flash('Account created successfully! Please login.')
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
            flash(f"Welcome, {user['username']}!")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('login'))
    return render_template('login.html')






# ---------------------------------------- #

if __name__ == '__main__':
    app.run(debug=True)

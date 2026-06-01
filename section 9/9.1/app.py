from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import init_db, get_db_connection
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secter123'
init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if not username or not email or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username,email)).fetchone()
        conn.close()
        if user:
            flash('Username or email already exists!', 'error')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful!, please login', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already esixts!', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Please enter both username and passworde!', 'error')
            return redirect(url_for('login'))
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username =?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']            
            session['email'] = user['email']
            flash(f"Welcome back, {username}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access this page!', 'error')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], email=session['email'])

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
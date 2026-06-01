from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from database import init_db, get_db_connection
from datetime import timedelta, datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secter123'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = False 
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
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
            session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            session['login_ip'] = request.remote_addr
            session['user_agent'] = request.user_agent.string
            session.permanent = True
            flash(f"Welcome back, {username}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/session-info')
def session_info():
    if 'user_id' not in session:
        flash('Please login to view session information!', 'error')
        return redirect(url_for('login'))
    session_age = None
    if 'login_time' in session:
        login_time = datetime.strptime(session['login_time'], '%Y-%m-%d %H:%M:%S')
        session_age = (datetime.now() - login_time).total_seconds() / 60
    session_data = {
        'session_id': session.get('_id', 'N/A'),
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'email': session.get('email'),
        'login_time': session.get('login_time'),
        'login_ip': session.get('login_ip'),
        'user_agent': session.get('user_agent'),
        'session_age_minutes':round(session_age, 2) if session_age else 0,
        'session_permanent':session.permanent,
        'session_expiry':(datetime.now() + app.permanent_session_lifetime).strftime('%Y-%m-%d %H:%M:%S') if session.permanent else 'Not Set'

    }
    return render_template('session_info.html', session_data=session_data)



@app.route('/extend-session')
def extend_session():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    session['last_activity'] = datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S'
    )
    session.permanent = True
    flash('Session extended successfully!', 'success')
    return redirect(url_for('session_info'))


@app.route('/active-sessions')
def active_sessions():
    if 'user_id' not in session:
        flash('Please login to view active sessions!', 'error')
        return redirect(url_for('login'))
    current_session = {
        'session_id': session.get('_id', 'N/A'),
        'browser': session.get('user_agent', 'Unknown')[:50],
        'ip':session.get('login_pd', 'Unknown'),
        'login_time':session.get('login_time', 'Unknown'),
        'current':True
    }
    return render_template('active_session.html', sessions=[current_session])



@app.before_request
def check_session_timeout():
    if request.endpoint in ['home', 'login', 'register', 'static']:
        return
    if 'user_id' in session:
        last_activity = session.get('last_activity')
        if not last_activity:
            session['last_activity'] = datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S'
            )
            return
        last_activity_time = datetime.strptime(
            last_activity,
            '%Y-%m-%d %H:%M:%S'
        )
        inactive_minutes = (
            datetime.now() - last_activity_time
        ).total_seconds() / 60
        if inactive_minutes > 30:
            session.clear()
            flash(
                'Your session has expired due to inactivity. Please login again.',
                'error'
            )
            return redirect(url_for('login'))
        session['last_activity'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'
        )


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
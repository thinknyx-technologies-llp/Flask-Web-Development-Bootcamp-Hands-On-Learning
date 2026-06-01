from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from database import init_db, get_db_connection, get_user_role, get_user_permissions, has_permission
from functools import wraps
from datetime import timedelta, datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secret123'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page!', 'error')
                return redirect(url_for('login'))
            user_role = session.get('role_name')
            if user_role not in roles:
                flash(f'Access denied. Required role: {", ".join(roles)}', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permissions_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page!', 'error')
                return redirect(url_for('login'))
            if not has_permission(session['user_id'], permission):
                flash(f'Access denied. Required permission: {permission}', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


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
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwordsdo not match!', 'error')
            return redirect(url_for('register'))
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE  username = ? OR email = ?', (username, email)).fetchone()
        if user:
            conn.close()
            flash('Username or email already exists!','error')
            return redirect(url_for('register'))
        default_role = conn.execute('SELECT id FROM roles WHERE role_name = "user"').fetchone()
        hashed_password = generate_password_hash(password)
        try:
            conn.execute('INSERT INTO users (username, email, password, role_id) VALUES (?,?,?,?)', (username, email, hashed_password, default_role['id'] if default_role else None))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            flash('Username or email already exists!', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Please enter both username and password!', 'error')
            return redirect(url_for('login'))
        conn = get_db_connection()
        user = conn.execute('''SELECT u.*, r.role_name, r.description as role_description FROM users u LEFT JOIN roles r ON u.role_id = r.id WHERE u.username = ?''', (username,)).fetchone()
        conn.close()
        if user and user['is_active'] and check_password_hash(user['password'],password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role_id'] = user['role_id']
            session['role_name'] = user['role_name']
            session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            session['login_ip'] = request.remote_addr
            session['permissions'] = get_user_permissions(user['id'])
            session.permanent = True
            flash(f'Welcome {username}! You are logged in as {user["role_name"]}.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_role = session.get('role_name')
    permissions = session.get('permissions', [])
    users = None
    if 'view_users' in permissions:
        conn = get_db_connection()
        users = conn.execute('''
            SELECT u.id, u.username, u.email, u.is_active, r.role_name, u.created_at 
            FROM users u 
            LEFT JOIN roles r ON u.role_id = r.id
            ORDER BY u.id
        ''').fetchall()
        conn.close()
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         email=session['email'],
                         role=user_role,
                         permissions=permissions,
                         users=users)

@app.route('/admin/users')
@login_required
@permissions_required('view_users')
def manage_users():
    conn = get_db_connection()
    users = conn.execute('''SELECT u.id, u.username, u.email, u.is_active, r.role_name, u.created_at FROM users u LEFT JOIN roles r ON u.role_id = r.id ORDER BY u.id''').fetchall()
    roles = conn.execute('SELECT id, role_name FROM roles').fetchall()
    conn.close()
    return render_template('manage_users.html', users=users, roles=roles)

@app.route('/admin/users/creaste', methods=['GET','POST'])
@login_required
@permissions_required('create_users')
def create_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    role_id = request.form['role_id']
    if not username or not email or not password:
        flash('All fields are required!', 'error')
        return redirect(url_for('manage_users'))
    conn = get_db_connection()
    hashed_password = generate_password_hash(password)
    try:
        conn.execute('INSERT INTO users (username, email, password, role_id) VALUES (?,?,?,?)', (username, email, hashed_password, role_id))
        conn.commit()
        flash('User create successfully!','success')
    except sqlite3.IntegrityError:
        flash('Username or email already exists!', 'error')
    finally:
        conn.close()
    return redirect(url_for('manage_users'))


@app.route('/admin/users/<int:user_id>/edit', methods=['GET','POST'])
@login_required
@permissions_required('edit_users')
def edit_user(user_id):
    role_id = request.form['role_id']
    is_active = request.form.get('is_active') == 'on'
    conn = get_db_connection()
    conn.execute('UPDATE users SET role_id = ?, is_active = ? WHERE id = ?', (role_id, is_active, user_id))
    conn.commit()
    conn.close()
    flash('User updated successfully!','success')
    return redirect(url_for('manage_users'))

@app.route('/admin/users/<int:user_id>/delete', methods=['GET','POST']) 
@login_required
@permissions_required('delete_users')
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('manage_users'))
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id))
    conn.commit()
    conn.close()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/roles')
@login_required
@permissions_required('manage_roles')
def manage_roles():
    conn = get_db_connection()
    roles = conn.execute('SELECT * FROM roles').fetchall()
    permissions = conn.execute('SELECT * FROM permissions').fetchall()
    role_permissions = {}
    for role in roles:
        perms = conn.execute('''
            SELECT p.id, p.permission_name 
            FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            WHERE rp.role_id = ?
        ''', (role['id'],)).fetchall()
        role_permissions[role['id']] = [p['permission_name'] for p in perms]    
    conn.close()
    return render_template('manage_roles.html', roles=roles, permissions=permissions,role_permissions=role_permissions)

@app.route('/admin/roles/<int:role_id>/permissions', methods=['POST'])
@login_required
@permissions_required('manage_roles')
def update_role_permissions(role_id):
    permission_ids = request.form.getlist('permissions')
    conn = get_db_connection()
    conn.execute('DELETE FROM role_permissions WHERE role_id = ?', (role_id,))
    for perm_id in permission_ids:
        conn.execute('INSERT INTO role_permissions (role_id, permission_id) VALUES (?,?)', (role_id,perm_id))
    conn.commit()
    conn.close()
    flash('Role permissions updated successfully!', 'success')
    return redirect(url_for('manage_roles'))

@app.route('/reports')
@login_required
@permissions_required('view_reports')
def reports():
    conn = get_db_connection()
    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    active_users = conn.execute('SELECT COUNT(*) as count FROM users WHERE is_active = 1').fetchone()['count']
    role_distribution = conn.execute('''SELECT r.role_name, COUNT(u.id) as count FROM roles r LEFT JOIN users u ON r.id = u.role_id GROUP BY r.id''').fetchall()
    conn.close()
    return render_template('reports.html', total_users=total_users,active_users=active_users,role_distribution=role_distribution)

@app.route('/logs')
@login_required
@permissions_required('view_logs')
def view_logs():
    logs = [
        {'timestamp':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
         'user':session['username'],
         'action':'Viewed logs',
         'ip':session.get('login_ip')}
    ]
    return render_template('logs.html',logs=logs)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', username=session['username'],email=session['email'],role=session.get('role_name'))


@app.route('/profile/edit', methods=['GET','POST'])
@login_required
@permissions_required('edit_profile')
def edit_profile():
    email = request.form['email']
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if email:
        try:
            conn.execute('UPDATE users SET email = ? WHERE id = ?', email, session['user_id'])
            session['email'] = email
            flash('Email update successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Email alreadyexists!', 'error')

    if current_password and new_password:
        if check_password_hash(user['password'], current_password):
            hashed_password = generate_password_hash(new_password)
            conn.execute('Update users SET password = ? WHERE id = ?', (hashed_password, session['user_id']))
            flash('Password update successfully!', 'success')
        else:
            flash('Crrent password is incorrect', 'error')
    conn.commit()
    conn.close()
    return redirect(url_for('profile'))

@app.route('/session-info')
@login_required
def session_info():
    session_age = None
    if 'login_time' in session:
        login_time = datetime.strptime(session['login_time'], '%Y-%m-%d %H:%M:%S')
        session_age = (datetime.now() - login_time).total_seconds() / 60
    session_data = {
        "user_id":session.get('user_id'),
        "username":session.get('username'),
        "email":session.get('email'),
        "role_name":session.get('role_name'),
        "permissions":session.get('permissions',[]),
        "login_time":session.get('login_time'),
        "login_ip":session.get('login_ap'),
        'session_age_minutes': round(session_age, 2) if session_age else None,
        'session_permanent': session.permanent,
        'session_expiry': (datetime.now() + app.permanent_session_lifetime.strftime('%Y-%m-%d %H:%M:%S'))
    }
    return render_template('session_info.html', session_data=session_data)

@app.route('/extended-session')
@login_required
def extended_session():
    session.permanent = True
    session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    flash('Session extended successfully!', 'success')
    return redirect(url_for('session_info'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('home'))

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
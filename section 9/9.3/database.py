import sqlite3
import os
from werkzeug.security import generate_password_hash

def get_db_connection():
    conn = sqlite3.connect('instance/users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs('instance', exist_ok=True)
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            permission_name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id INTEGER,
            permission_id INTEGER,
            FOREIGN KEY (role_id) REFERENCES roles (id),
            FOREIGN KEY (permission_id) REFERENCES permissions (id),
            PRIMARY KEY (role_id, permission_id)
        )
    ''')
    default_roles = [
        ('admin', 'Administrator with full access'),
        ('manager', 'Manager with moderate access'),
        ('user', 'Regular user with basic access'),
        ('viewer', 'Read-only access')
    ]
    
    for role_name, description in default_roles:
        conn.execute('INSERT OR IGNORE INTO roles (role_name, description) VALUES (?, ?)',
                    (role_name, description))
    default_permissions = [
        ('view_dashboard', 'Can view dashboard'),
        ('edit_profile', 'Can edit own profile'),
        ('view_users', 'Can view all users'),
        ('create_users', 'Can create new users'),
        ('edit_users', 'Can edit any user'),
        ('delete_users', 'Can delete users'),
        ('manage_roles', 'Can manage roles and permissions'),
        ('view_reports', 'Can view reports'),
        ('manage_settings', 'Can manage system settings'),
        ('view_logs', 'Can view system logs')
    ]
    
    for perm_name, description in default_permissions:
        conn.execute('INSERT OR IGNORE INTO permissions (permission_name, description) VALUES (?, ?)',
                    (perm_name, description))
    admin_role = conn.execute('SELECT id FROM roles WHERE role_name = "admin"').fetchone()
    manager_role = conn.execute('SELECT id FROM roles WHERE role_name = "manager"').fetchone()
    user_role = conn.execute('SELECT id FROM roles WHERE role_name = "user"').fetchone()
    viewer_role = conn.execute('SELECT id FROM roles WHERE role_name = "viewer"').fetchone()
    permissions = {}
    for perm_name, _ in default_permissions:
        perm = conn.execute('SELECT id FROM permissions WHERE permission_name = ?', (perm_name,)).fetchone()
        if perm:
            permissions[perm_name] = perm['id']

    conn.execute('DELETE FROM role_permissions')
    if admin_role:
        for perm_id in permissions.values():
            conn.execute('INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)',
                        (admin_role['id'], perm_id))
    if manager_role:
        manager_perms = ['view_dashboard', 'edit_profile', 'view_users', 'create_users', 
                        'edit_users', 'view_reports', 'view_logs']
        for perm_name in manager_perms:
            if perm_name in permissions:
                conn.execute('INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)',
                            (manager_role['id'], permissions[perm_name]))
    if user_role:
        user_perms = ['view_dashboard', 'edit_profile']
        for perm_name in user_perms:
            if perm_name in permissions:
                conn.execute('INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)',(user_role['id'], permissions[perm_name]))
    if viewer_role:
        viewer_perms = ['view_dashboard', 'view_reports']
        for perm_name in viewer_perms:
            if perm_name in permissions:
                conn.execute('INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)',(viewer_role['id'], permissions[perm_name]))
    admin_password = generate_password_hash('admin123')
    conn.execute('''INSERT OR IGNORE INTO users (username, email, password, role_id, is_active) 
        VALUES (?, ?, ?, ?, ?)''', ('admin', 'admin@example.com', admin_password, admin_role['id'] if admin_role else None, 1))
    manager_password = generate_password_hash('manager123')
    conn.execute('''INSERT OR IGNORE INTO users (username, email, password, role_id, is_active) 
        VALUES (?, ?, ?, ?, ?)''', ('manager', 'manager@example.com', manager_password, manager_role['id'] if manager_role else None, 1))
    user_password = generate_password_hash('user123')
    conn.execute('''INSERT OR IGNORE INTO users (username, email, password, role_id, is_active) 
        VALUES (?, ?, ?, ?, ?)''', ('user', 'user@example.com', user_password, user_role['id'] if user_role else None, 1))
    conn.commit()
    conn.close()
    print("Database initialized successfully with roles and permissions!")
    print("\nDefault Login Credentials:")
    print("Admin    - Username: admin, Password: admin123")
    print("Manager  - Username: manager, Password: manager123")
    print("User     - Username: user, Password: user123")

def get_user_role(user_id):
    conn = get_db_connection()
    user = conn.execute('''SELECT u.*, r.role_name, r.description as role_description FROM users u LEFT JOIN roles r ON u.role_id = r.id WHERE u.id = ?''', (user_id,)).fetchone()
    conn.close()
    return user

def get_user_permissions(user_id):
    conn = get_db_connection()
    permissions = conn.execute('''
        SELECT DISTINCT p.permission_name 
        FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        JOIN users u ON rp.role_id = u.role_id
        WHERE u.id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return [perm['permission_name'] for perm in permissions]

def has_permission(user_id, permission_name):
    permissions = get_user_permissions(user_id)
    return permission_name in permissions

if __name__ == '__main__':
    init_db()
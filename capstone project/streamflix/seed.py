"""
Run this once to create the first admin user.
Usage: python seed.py
"""
from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    db.create_all()

    # Check if admin already exists
    existing = User.query.filter_by(email='admin@streamflix.com').first()
    if existing:
        print('Admin already exists.')
    else:
        admin = User(
            username='admin',
            email='admin@streamflix.com',
            is_admin=True
        )
        admin.set_password('admin123')   # <-- change this!
        db.session.add(admin)
        db.session.commit()
        print('✓ Admin created: admin@streamflix.com / admin123')
        print('  ⚠️  Change the password after first login!')

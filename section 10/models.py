from extensions import db
from werkzeug.security import generate_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


def create_admin():
    admin_exists = User.query.filter_by(username='admin').first()

    if not admin_exists:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin'
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully!")
    else:
        print("Admin already exists.")
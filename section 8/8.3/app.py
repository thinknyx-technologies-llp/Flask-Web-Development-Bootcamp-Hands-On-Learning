from flask import Flask, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

 
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

with app.app_context():
    db.create_all()
    admin_name = os.getenv('ADMIN_USERNAME')
    if not User.query.filter_by(username=admin_name).first():
        print(f"Creating admin user: {admin_name}")
        new_admin = User(
            username = admin_name,
            email=os.getenv('ADMIN_EMAIL'),
            password_hash = generate_password_hash(os.getenv('ADMIN_PASSWORD'))
        )
        db.session.add(new_admin)
        db.session.commit()

@app.route('/users')
def get_users():
    users = User.query.all()
    return jsonify([
        {"id":u.id, "username":u.username, "email":u.email}
        for u in users
    ])



 
if __name__ == '__main__':
    app.run(debug=True)
 
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate
 
load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///project.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.String(200))

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)
 
@app.route('/add', methods=['POST'])
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('index'))
 
# 2. UPDATE
@app.route('/update/<int:id>', methods=['POST'])
def update_user(id):
    user = User.query.get_or_404(id)
    user.username = request.form.get('username')
    user.email = request.form.get('email')
    db.session.commit()
    return redirect(url_for('index'))
 
# 3. DELETE
@app.route('/delete/<int:id>')
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('index'))
 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
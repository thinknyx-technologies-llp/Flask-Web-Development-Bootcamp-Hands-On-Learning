from flask import Flask, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import create_admin
from extensions import db, migrate
from models import User, Assignment
from forms import RegisterForm, LoginForm, AssignmentForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student.db'


db.init_app(app)
migrate.init_app(app, db)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)

        user = User(
            username=form.username.data,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['role'] = user.role

            return redirect(url_for('dashboard'))

    return render_template('login.html', form=form)


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    assignments = Assignment.query.filter_by(user_id=session['user_id']).all()

    return render_template('dashboard.html', assignments=assignments)

@app.route('/add', methods=['GET', 'POST'])
def add_assignment():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    form = AssignmentForm()

    if form.validate_on_submit():
        assignment = Assignment(
            title=form.title.data,
            subject=form.subject.data,
            user_id=session['user_id']
        )

        db.session.add(assignment)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('add_assignment.html', form=form)


@app.route('/delete/<int:id>')
def delete_assignment(id):
    assignment = Assignment.query.get(id)

    db.session.delete(assignment)
    db.session.commit()

    return redirect(url_for('dashboard'))


@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return 'Access Denied'

    assignments = Assignment.query.all()

    return render_template('admin.html', assignments=assignments)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)
from flask import Blueprint, render_template, redirect, url_for, flash
from app.auth.forms import RegisterForm, LoginForm
from app.models import User
from app.extensions import db
from flask_login import login_user, logout_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        existing_user = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_user:

            flash("Email already exists")

            return redirect(url_for("auth.register"))

        user = User(
            username=form.username.data,
            email=form.email.data
        )

        user.set_password(form.password.data)

        db.session.add(user)

        db.session.commit()

        flash("Registration Successful")

        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and user.check_password(form.password.data):

            login_user(user)

            flash("Login Successful")

            return redirect(url_for("tasks.dashboard"))

        else:

            flash("Invalid Email or Password")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
def logout():

    logout_user()

    flash("Logged Out")

    return redirect(url_for("auth.login"))
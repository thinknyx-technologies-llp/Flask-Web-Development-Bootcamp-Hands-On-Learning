from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.tasks.forms import TaskForm
from app.models import Task
from app.extensions import db

task_bp = Blueprint("tasks", __name__)

@task_bp.route("/")
@login_required
def dashboard():

    tasks = Task.query.filter_by(owner=current_user)

    return render_template("dashboard.html", tasks=tasks)


@task_bp.route("/add-task", methods=["GET", "POST"])
@login_required
def add_task():

    form = TaskForm()

    if form.validate_on_submit():

        task = Task(
            title=form.title.data,
            owner=current_user
        )

        db.session.add(task)
        db.session.commit()

        return redirect(url_for("tasks.dashboard"))

    return render_template("tasks.html", form=form)
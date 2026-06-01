from flask import Blueprint, jsonify
from app.models import Task

api_bp = Blueprint("api", __name__)

@api_bp.route("/api/tasks")
def get_tasks():

    tasks = Task.query.all()

    data = []

    for task in tasks:

        data.append({
            "id": task.id,
            "title": task.title,
            "completed": task.completed
        })

    return jsonify(data)
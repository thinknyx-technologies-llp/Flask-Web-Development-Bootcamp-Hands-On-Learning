from flask import Flask, request, redirect, url_for, render_template, jsonify

app = Flask(__name__)

tasks = [
    {"id": 1, "title": "Learn Flask", "completed": False},
    {"id": 2, "title": "Build a project", "completed": False}
]

def find_task(task_id):
    return next((task for task in tasks if task["id"] == task_id), None)

@app.route('/')
def home():
    return redirect(url_for('list_tasks_html'))

@app.route('/tasks', methods=['GET', 'POST'])
def list_tasks_html():
    if request.method == 'POST':
        title = request.form.get('title')
        if not title:
            return "Title is required", 400
        
        new_id = max([t["id"] for t in tasks], default=0) + 1
        tasks.append({"id": new_id, "title": title, "completed": False})
        return redirect(url_for('list_tasks_html'))
    
    return render_template('tasks.html', tasks=tasks)

@app.route('/api/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_task_api(task_id):
    task = find_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if request.method == 'GET':
        return jsonify(task)
    
    elif request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        task['title'] = data.get('title', task['title'])
        task['completed'] = data.get('completed', task['completed'])
        return jsonify(task)
    
    elif request.method == 'DELETE':
        tasks.remove(task)
        return jsonify({"message": "Task deleted"}), 200

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks_json():
    completed_filter = request.args.get('completed')
    if completed_filter is not None:
        filtered = [t for t in tasks if str(t['completed']).lower() == completed_filter.lower()]
        return jsonify(filtered)
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task_json():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Title required"}), 400
    
    new_id = max([t["id"] for t in tasks], default=0) + 1
    new_task = {
        "id": new_id,
        "title": data['title'],
        "completed": data.get('completed', False)
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

@app.route('/tasks/<int:task_id>/update', methods=['POST'])
def update_task_form(task_id):
    task = find_task(task_id)
    if not task:
        return "Task not found", 404
    
    new_title = request.form.get('title')
    if new_title:
        task['title'] = new_title
    
    completed = request.form.get('completed')
    task['completed'] = completed == 'on'
    
    return redirect(url_for('list_tasks_html'))

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task_form(task_id):
    global tasks
    task = find_task(task_id)
    if task:
        tasks.remove(task)
    return redirect(url_for('list_tasks_html'))

if __name__ == '__main__':
    app.run(debug=True)

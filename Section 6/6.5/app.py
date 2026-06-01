from flask import Flask, render_template

app = Flask(__name__)


@app.context_processor
def inject_global():
    return {"site_name":"Thinknyx Task Master"}


@app.route('/tasks')
def task_list():
    tasks = [
        {"name":"Fix Login Bug", "priority":"High", "done":True},
        {"name":"Update Documentation", "priority":"Low", "done":False},
        {"name":"API Integration", "priority":"Medium", "done":False},
        {"name":"Database Migration", "priority":"High", "done":False},
    ]
    return render_template('task.html', tasks = tasks, user_role = "manager")



if __name__ == '__main__':
    app.run(debug=True)
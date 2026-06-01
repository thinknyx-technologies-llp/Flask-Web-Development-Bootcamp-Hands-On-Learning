from flask import Flask, render_template
from datetime import datetime
app = Flask(__name__)

@app.context_processor
def inject_global_vars():
    return {
        "site_name": "DevPortal 2026",
        "current_year": datetime.now().year
    }

@app.route('/')
def index():
    user_data = {
        "name":"Alex",
        "role":"Lead Developer",
        "skills":["Python", "Flask", "Jinja2"]
    }
    return render_template('index.html', user = user_data)

if __name__ == "__main__":
    app.run(debug=True)
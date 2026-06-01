from flask import Flask
from authentication import auth
from blogs import blog

app = Flask(__name__)

app.register_blueprint(auth)
app.register_blueprint(blog)

@app.route('/')
def home():
    return "This is the home page of the application."

if __name__ == "__main__":
    app.run(debug=True)
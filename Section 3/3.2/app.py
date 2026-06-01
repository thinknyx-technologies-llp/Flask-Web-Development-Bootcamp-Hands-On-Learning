from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/pageone")
def pageone():
    return render_template("pageone.html")

@app.route("/pagetwo")
def pagetwo():
    return render_template("pagetwo.html")

@app.route('/allow/<word>')
def checking(word):
    if word == "admin":
        return render_template('allowed.html')
    if word == "user":
        return render_template('notallowed.html')

if __name__ == "__main__":
    app.run(debug=True)
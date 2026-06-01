from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/go-to-success')
def go_to_success():
    return redirect(url_for('success_page'))

@app.route('/welcome')
def success_page():
    return "<h1> Success! You have been redirected.</h1>"

if __name__ == "__main__":
    app.run(debug=True)
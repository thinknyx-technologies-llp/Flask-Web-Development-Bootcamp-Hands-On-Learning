from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

@app.route('/form', methods = ['GET', 'POST'])
def handle_form():
    if request.method == 'POST':
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        return f"Hello {first_name} {last_name}"
    return render_template("form.html")

if __name__ == '__main__':
    app.run(debug=True)
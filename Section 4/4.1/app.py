from flask import *
app = Flask(__name__)

@app.route('/')
def input():
    return render_template("temp.html")

@app.route('/passing', methods=['GET','POST'])
def display():
    if request.method == 'POST':
        result = request.form
        return render_template("result_data.html", result=result)
    

if __name__ == "__main__":
    app.run(debug = True)
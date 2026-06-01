from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    var1 = "Hello Thinknyx"
    number = 10
    final_value = var1 - number
    return final_value

if __name__ == "__main__":
    app.run(debug=False)
from flask import Flask, render_template, make_response

app = Flask(__name__)

@app.route('/welcome')
def welcome():
    response = make_response(render_template('index.html', name="Explore"), 200)
    response.headers['X-Custom-Header'] = 'Thinknyx-Technologies'
    return response

if __name__ == '__main__':
    app.run(debug=True)
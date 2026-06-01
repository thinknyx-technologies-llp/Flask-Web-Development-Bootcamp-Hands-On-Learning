from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    print(data)
    user_message = data.get('message', '')

    response_data = {
        "status": "success",
        "echo": user_message.upper(),
        "server_note": "JSON recieved and processed!"
    }
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True)
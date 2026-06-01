from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to Flask Testing"

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    return f"Welcome {data['username']}"

client = app.test_client()

response = client.get("/")
print(response.status_code)
print(response.data.decode())

response = client.post(
    "/login",
    json={
        "username": "admin"
    }
)

print(response.status_code)
print(response.data.decode())
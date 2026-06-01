from flask import Flask, jsonify
from unittest.mock import patch

app = Flask(__name__)

def get_user_from_db(user_id):
    return {"id": user_id, "name":"kanishk"}

@app.route("/user/<int:user_id>")
def get_user(user_id):
    user = get_user_from_db(user_id)
    return jsonify(user)

def test_get_user():
    with patch("test_app.get_user_from_db") as mock_db:
        mock_db.return_value = {
            "id":1,
            "name":"Mock User"
        }
        client = app.test_client()
        response = client.get("/user/1")

        assert response.status_code == 200
        assert response.json["name"] == "Mock User"
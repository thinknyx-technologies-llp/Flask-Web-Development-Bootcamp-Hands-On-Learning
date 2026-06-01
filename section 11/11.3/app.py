from flask import Flask, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

items = ["apple", "banana", "kiwi"]

class Item(Resource):
    def get(self):
        return {"items":items}
    
    def post(self):
        data = request.get_json()
        items.append(data["name"])
        return {"message":"Item added", "items":items}, 201
    
api.add_resource(Item, '/items')

if __name__ == "__main__":
    app.run(debug=True)
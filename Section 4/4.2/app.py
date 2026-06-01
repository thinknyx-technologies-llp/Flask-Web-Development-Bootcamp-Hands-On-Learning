from flask import Flask, request, jsonify

app = Flask(__name__)

products = [
    {"id":1, "name":"Laptop", "category":"electronics", "price":1200},
    {"id":1, "name":"Coffee Mug", "category":"kitchen", "price":15},
    {"id":1, "name":"headphones", "category":"electronics", "price":200}
]

@app.route('/products')
def get_products():
    category = request.args.get('category')
    max_price = request.args.get('max_price', type=int)
    results = products

    if category:
        results = [p for p in results if p['category'] == category]
    if max_price:
        results = [p for p in results if p['price'] <= max_price]

    return jsonify({
        "filters_applied": {"category": category, "max_price":max_price},
        "count": len(results),
        "products": results
    })

if __name__ == "__main__":
    app.run(debug=True)
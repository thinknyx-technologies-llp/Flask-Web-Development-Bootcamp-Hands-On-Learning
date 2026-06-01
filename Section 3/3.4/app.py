from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

user_profile = {"username":"dev_user", "email":"dev@thinknkyx.com"}

blog_posts = []

@app.route("/user", methods=['GET'])
def get_user():
    return jsonify(user_profile), 200


@app.route("/posts", methods=['POST'])
def create_post():
    data = request.get_json()
    blog_posts.append(data)
    return jsonify({"status":"Post created", "all_posts":blog_posts}), 201




@app.route("/<word>")
@app.route("/home/<word>")
@app.route("/index/<word>")
def index(word):
    word = word * 2
    return word

@app.route("/pageone")
def pageone():
    return render_template("pageone.html")

@app.route("/index/pagetwo")
def pagetwo():
    return render_template("pagetwo.html")


@app.route("/allow/<word>")
def checking(word):
    if word == "admin":
        return render_template("allowed.html")
    if word == "user":
        return render_template("not_allowed.html")

if __name__ == "__main__":
    app.run(debug=True)
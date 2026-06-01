from flask import Blueprint

blog = Blueprint('blog', __name__)

@blog.route('/blog')
def blog_page():
    return "This is the blog page."
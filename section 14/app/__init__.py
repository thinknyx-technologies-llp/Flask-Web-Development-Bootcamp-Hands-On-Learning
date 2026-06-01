from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    migrate.init_app(app, db)

    from app.auth.routes import auth_bp
    from app.tasks.routes import task_bp
    from app.api.routes import api_bp

    app.register_blueprint(auth_bp)

    app.register_blueprint(task_bp)

    app.register_blueprint(api_bp)

    return app
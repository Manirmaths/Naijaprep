# app/__init__.py
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request  # <-- add jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, CSRFError  # <-- add CSRFError
from flask_bcrypt import Bcrypt
from flask_mail import Mail

from flask_limiter import Limiter                 # <-- add
from flask_limiter.util import get_remote_address # <-- add

load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

# Global limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "60 per hour"],   # sane defaults
    storage_uri="memory://",                         # use Redis in prod
)

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)  # <-- enable limiter

    login_manager.login_view = "login"

    with app.app_context():
        from app.models import User, Question, UserResponse, ReviewQuestion  # noqa: F401
        db.create_all()
        from app.db_maintenance import ensure_indexes
        ensure_indexes()

    # CSRF error handler (works for fetch() and forms)
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e: CSRFError):
        wants_json = request.headers.get("Accept", "").find("application/json") >= 0 or \
                     request.headers.get("X-Requested-With") == "XMLHttpRequest"
        if wants_json:
            return jsonify({"status": "error", "message": "CSRF validation failed."}), 400
        return ("<h4>CSRF validation failed</h4>"
                "<p>Please refresh the page and try again.</p>", 400)

    # Make csrf_token easily available in all templates (for fetch headers)
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)

    from app import routes
    routes.init_routes(app)

    return app

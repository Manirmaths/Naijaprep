# app/__init__.py
import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_mail import Mail

# Load .env (harmless in prod, useful locally)
load_dotenv()

# Create extensions (no app bound yet)
db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Bind extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    # Flask-Login default login endpoint
    login_manager.login_view = "login"

    # Ensure models are registered
    with app.app_context():
        from app.models import User, Question, UserResponse, ReviewQuestion  # noqa: F401

    # Register routes on this app instance
    from app import routes
    routes.init_routes(app)

    return app

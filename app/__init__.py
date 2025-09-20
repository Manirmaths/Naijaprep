# app/__init__.py
import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_mail import Mail

# Load .env only for local dev; harmless on Heroku
load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    app = Flask(__name__)
    # pull EVERYTHING from Config
    app.config.from_object("config.Config")

    # init extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    # login view (adjust if you use blueprints)
    login_manager.login_view = "login"

    # register models so SQLAlchemy sees them
    with app.app_context():
        from app.models import User, Question, UserResponse, ReviewQuestion  # noqa: F401

    # register routes/blueprints
    from app import routes  # noqa: F401

    return app

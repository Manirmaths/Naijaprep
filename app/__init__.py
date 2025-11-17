# app/__init__.py
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_bcrypt import Bcrypt
from flask_mail import Mail

# --- Try to import Flask-Limiter, but don't hard-crash if missing ---
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
except ImportError:
    Limiter = None

    def get_remote_address():
        return None

    class _DummyLimiter:
        """
        No-op limiter so @limiter.limit(...) still works even if
        Flask-Limiter is not installed (e.g. on Railway right now).
        """
        def limit(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator

    limiter = _DummyLimiter()
else:
    # Real limiter instance when Flask-Limiter is available
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "60 per hour"],  # sane defaults
        storage_uri="memory://",                        # swap to Redis in real prod
    )

# Load .env (harmless in prod, useful locally)
load_dotenv()

# Extensions (unbound)
db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Bind extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    # Bind limiter only if it's a real Limiter, not the dummy
    if Limiter is not None:
        limiter.init_app(app)

    # Flask-Login default login endpoint
    login_manager.login_view = "login"

    with app.app_context():
        # Ensure models are registered
        from app.models import User, Question, UserResponse, ReviewQuestion  # noqa: F401

        # Create tables if they don't exist
        db.create_all()

        # Ensure performance indexes exist (safe/re-entrant)
        from app.db_maintenance import ensure_indexes
        ensure_indexes()

    # -------- CSRF error handling --------
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e: CSRFError):
        wants_json = (
            "application/json" in (request.headers.get("Accept") or "")
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        )
        if wants_json:
            return jsonify({"status": "error", "message": "CSRF validation failed."}), 400
        return (
            "<h4>CSRF validation failed</h4>"
            "<p>Please refresh the page and try again.</p>",
            400,
        )

    # Make csrf_token available in all templates (e.g. for fetch headers)
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)

    # Register routes
    from app import routes
    routes.init_routes(app)

    return app

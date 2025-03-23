from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_mail import Mail  # Add Flask-Mail
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'REDACTED_SECRET'  # Ensure this is a strong, unique key
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail configuration (example with Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'REDACTED_EMAIL'  # Replace with your Gmail address
app.config['MAIL_PASSWORD'] = 'REDACTED_PASSWORD'  # Replace with Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'REDACTED_EMAIL'

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)
mail = Mail(app)  # Initialize Flask-Mail

# Import models to register them with SQLAlchemy
from app.models import User, Question, UserResponse

# Create tables if they don’t exist
with app.app_context():
    db.create_all()

from app import routes
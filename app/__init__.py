from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)
# Import models to register them with SQLAlchemy
from app.models import User, Question, UserResponse

# Create tables if they don’t exist
with app.app_context():
    db.create_all()

from app import routes
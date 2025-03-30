from app import app, db
from app.models import Question, UserResponse
from sqlalchemy import text

with app.app_context():
    db.create_all()
    print("Table created successfully!")

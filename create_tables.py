# create_tables.py
from app import create_app, db
from app.models import User, Question, UserResponse, ReviewQuestion  # ensure models are imported

app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Database tables created (or already exist).")

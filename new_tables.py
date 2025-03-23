from app import app, db
from app.models import Question, UserResponse
from sqlalchemy import text

with app.app_context():
    # Drop the explanation column directly (PostgreSQL supports this)
    db.session.execute(text('ALTER TABLE question DROP COLUMN explanation'))
    db.session.commit()
    print("Explanation column dropped successfully!")
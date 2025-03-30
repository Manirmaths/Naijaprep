# check_db.py
from app import app, db
from app.models import Question

with app.app_context():
    question = Question.query.first()
    if question:
        print(f"First question explanation: {question.explanation}")
    else:
        print("No questions found.")
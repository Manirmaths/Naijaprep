from app import app
from app.models import Question
with app.app_context():
    print("Questions in DB:", Question.query.count())

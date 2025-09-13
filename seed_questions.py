# seed_questions.py
import csv
from app import app, db
from app.models import Question, UserResponse

with app.app_context():
    db.session.query(UserResponse).delete()
    db.session.query(Question).delete()
    db.session.commit()

    with open('questions3.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            question = Question(
                topic=row['topic'],
                difficulty=int(row['difficulty']),
                question_text=row['question_text'],
                option_a=row['option_a'],
                option_b=row['option_b'],
                option_c=row['option_c'],
                option_d=row['option_d'],
                correct_option=row['correct_option'],
                explanation=row.get('explanation', ''),
                exam_year=row.get('exam_year') or None  # new field handling
            )
            db.session.add(question)
        db.session.commit()
    print(f"Seeded {Question.query.count()} questions from questions3.csv!")
 
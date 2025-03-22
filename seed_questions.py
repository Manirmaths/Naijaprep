import csv
from app import app, db
from app.models import Question, UserResponse

with app.app_context():
    # Delete dependent UserResponse records first
    db.session.query(UserResponse).delete()
    # Then delete all Question records
    db.session.query(Question).delete()
    db.session.commit()  # Commit the deletions

    # Seed new questions from CSV
    with open('questions.csv', newline='', encoding='utf-8') as csvfile:
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
                explanation=row.get('explanation', '')
            )
            db.session.add(question)
        db.session.commit()
    print(f"Seeded {Question.query.count()} questions from CSV!")
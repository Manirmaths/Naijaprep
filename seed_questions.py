import csv
from app import app, db
from app.models import Question

with app.app_context():
    db.create_all()

    # Clear existing questions (optional, comment out if appending)
    db.session.query(Question).delete()
    db.session.commit()

    questions = []
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
                explanation=row['explanation']
            )
            questions.append(question)

    db.session.add_all(questions)
    db.session.commit()
    print(f"Seeded {len(questions)} questions from CSV!")
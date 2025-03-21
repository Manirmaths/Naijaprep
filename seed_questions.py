from app import app, db
from app.models import Question

with app.app_context():
    # Drop existing tables and recreate them (optional, only if you want a fresh start)
    db.drop_all()
    db.create_all()

    # Add sample questions
    q1 = Question(topic="Algebra", difficulty=1, question_text="What is 2 + 2?", 
                  option_a="3", option_b="4", option_c="5", option_d="6", correct_option="B")
    q2 = Question(topic="Geometry", difficulty=2, question_text="What is the area of a circle with radius 3?", 
                  option_a="9π", option_b="6π", option_c="3π", option_d="12π", correct_option="A")
    q3 = Question(topic="Arithmetic", difficulty=1, question_text="What is 10% of 100?", 
                  option_a="10", option_b="20", option_c="30", option_d="40", correct_option="A")

    # Add to database
    db.session.add_all([q1, q2, q3])
    db.session.commit()

    # Verify
    print("Questions added successfully:")
    for q in Question.query.all():
        print(f"- {q}")
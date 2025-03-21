from app import app, db
from app.models import Question

with app.app_context():
    
    db.create_all()

    questions = [
        Question(topic="Algebra", difficulty=2, question_text="Solve: 2x + 3 = 7", 
                 option_a="1", option_b="2", option_c="3", option_d="4", 
                 correct_option="B", explanation="Subtract 3 from both sides: 2x = 4, then divide by 2: x = 2."),
        Question(topic="Geometry", difficulty=1, question_text="Area of triangle, base 5, height 6?", 
                 option_a="15", option_b="30", option_c="12", option_d="18", 
                 correct_option="A", explanation="Area = ½ × base × height = ½ × 5 × 6 = 15."),
        Question(topic="Statistics", difficulty=1, question_text="Mean of 2, 4, 6, 8?", 
                 option_a="4", option_b="5", option_c="6", option_d="7", 
                 correct_option="B", explanation="Sum = 2 + 4 + 6 + 8 = 20, then divide by 4: 20 / 4 = 5."),
    ]
    db.session.add_all(questions)
    db.session.commit()
    print("Seeded questions with explanations!")

    # seed_questions.py
from app import app, db
from app.models import Question

with app.app_context():
    db.create_all()

    questions = [
        Question(topic="Algebra", difficulty=2, question_text="Solve: 2x + 3 = 7", 
                 option_a="1", option_b="2", option_c="3", option_d="4", 
                 correct_option="B", explanation="Subtract 3 from both sides: 2x = 4, then divide by 2: x = 2."),
        Question(topic="Algebra", difficulty=3, question_text="Solve: 3x - 5 = 10", 
                 option_a="3", option_b="5", option_c="7", option_d="9", 
                 correct_option="B", explanation="Add 5 to both sides: 3x = 15, then divide by 3: x = 5."),
        Question(topic="Geometry", difficulty=1, question_text="Area of triangle, base 5, height 6?", 
                 option_a="15", option_b="30", option_c="12", option_d="18", 
                 correct_option="A", explanation="Area = ½ × base × height = ½ × 5 × 6 = 15."),
        Question(topic="Geometry", difficulty=2, question_text="Perimeter of a square with side 4?", 
                 option_a="12", option_b="16", option_c="20", option_d="24", 
                 correct_option="B", explanation="Perimeter = 4 × side = 4 × 4 = 16."),
        Question(topic="Statistics", difficulty=1, question_text="Mean of 2, 4, 6, 8?", 
                 option_a="4", option_b="5", option_c="6", option_d="7", 
                 correct_option="B", explanation="Sum = 20, then divide by 4: 20 / 4 = 5."),
        Question(topic="Statistics", difficulty=2, question_text="Median of 1, 3, 5, 7, 9?", 
                 option_a="3", option_b="4", option_c="5", option_d="6", 
                 correct_option="C", explanation="Middle value of 1, 3, 5, 7, 9 is 5."),
    ]
    db.session.add_all(questions)
    db.session.commit()
    print("Seeded questions with explanations!")
    
    
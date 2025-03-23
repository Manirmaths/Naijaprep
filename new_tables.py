from app import app, db
from app.models import Question, UserResponse
from sqlalchemy import text

with app.app_context():
    # Backup current data into a temporary table
    db.session.execute(text('CREATE TABLE temp_question (id INTEGER PRIMARY KEY, topic VARCHAR(100) NOT NULL, difficulty INTEGER NOT NULL, question_text TEXT NOT NULL, option_a VARCHAR(100) NOT NULL, option_b VARCHAR(100) NOT NULL, option_c VARCHAR(100) NOT NULL, option_d VARCHAR(100) NOT NULL, correct_option VARCHAR(10) NOT NULL)'))
    db.session.execute(text('INSERT INTO temp_question (id, topic, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option) SELECT id, topic, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option FROM question'))
    db.session.execute(text('DROP TABLE question'))
    db.session.execute(text('ALTER TABLE temp_question RENAME TO question'))
    db.session.commit()  # Commit the transaction

    # Recreate foreign key relationships
    db.create_all()
    print("Explanation column dropped and table updated successfully!")
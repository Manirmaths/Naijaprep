# app/models.py
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), nullable=False)        # was 100
    difficulty = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    correct_option = db.Column(db.String(10), nullable=False) # keep 10
    explanation = db.Column(db.Text, nullable=True)
    exam_year = db.Column(db.String(255), nullable=True)      # was 50/100
    def __repr__(self):
        return f"Question('{self.topic}', '{self.difficulty}')"

class UserResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('responses', lazy=True))
    question = db.relationship('Question', backref=db.backref('responses', lazy=True))

    def __repr__(self):
        return f"UserResponse(User: {self.user_id}, Question: {self.question_id}, Correct: {self.is_correct})"

class ReviewQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('review_questions', lazy=True))
    question = db.relationship('Question', backref=db.backref('review_questions', lazy=True))

    def __repr__(self):
        return f"ReviewQuestion(User: {self.user_id}, Question: {self.question_id})"
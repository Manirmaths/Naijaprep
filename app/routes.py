from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db, bcrypt, mail
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Question, UserResponse, ReviewQuestion
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from random import choice
from sqlalchemy.exc import IntegrityError
import random
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

# Existing Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class QuizForm(FlaskForm):
    answer = RadioField('Answer', choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], validators=[DataRequired()])
    submit = SubmitField('Next')

# New Forms
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

# Token generation for password reset
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):  # 1 hour expiration
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except:
        return None
    return email

# Existing Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username or email already taken. Please choose a different one.', 'danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(f"Request method: {request.method}")  # Debug
    if form.validate_on_submit():
        print("Form validated successfully")  # Debug
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            print("User logged in, redirecting to home")  # Debug
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    else:
        if request.method == 'POST':
            print("Form validation failed:", form.errors)  # Debug
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    # Initialize quiz session if not already started
    if 'quiz_questions' not in session:
        responses = UserResponse.query.filter_by(user_id=current_user.id).all()
        topic_stats = {}
        for r in responses:
            topic = r.question.topic
            if topic not in topic_stats:
                topic_stats[topic] = {'correct': 0, 'total': 0}
            topic_stats[topic]['total'] += 1
            if r.is_correct:
                topic_stats[topic]['correct'] += 1

        all_questions = Question.query.all()
        if len(all_questions) < 3:
            flash('Not enough questions available. Please add more questions.', 'warning')
            return redirect(url_for('home'))

        # Select 3 unique questions
        if topic_stats:
            weakest_topic = min(topic_stats, key=lambda t: topic_stats[t]['correct'] / max(1, topic_stats[t]['total']))
            candidates = [q for q in all_questions if q.topic == weakest_topic]
            if len(candidates) >= 3:
                selected_questions = random.sample(candidates, 3)
            else:
                remaining = [q for q in all_questions if q not in candidates]
                selected_questions = candidates + random.sample(remaining, 3 - len(candidates))
        else:
            selected_questions = random.sample(all_questions, 3)

        session['quiz_questions'] = [q.id for q in selected_questions]
        session['current_question'] = 0
        session['score'] = 0

    # Get current question index and check if quiz is complete
    current_idx = session['current_question']
    if current_idx >= len(session['quiz_questions']):
        score = session['score']
        total = len(session['quiz_questions'])
        session.pop('quiz_questions', None)
        session.pop('current_question', None)
        session.pop('score', None)
        flash(f'Quiz completed! Your score: {score}/{total}', 'success')
        return redirect(url_for('results'))

    # Load current question and form
    question = Question.query.get(session['quiz_questions'][current_idx])
    form = QuizForm()

    if form.validate_on_submit():
        selected = form.answer.data
        is_correct = (selected == question.correct_option)
        response = UserResponse(
            user_id=current_user.id,
            question_id=question.id,
            selected_option=selected,
            is_correct=is_correct
        )
        db.session.add(response)
        if is_correct:
            current_user.points += 10
            session['score'] += 1
        db.session.commit()
        session['current_question'] += 1
        return redirect(url_for('quiz'))

    return render_template('quiz.html', question=question, form=form, current=current_idx + 1, total=len(session['quiz_questions']))

@app.route('/results')
@login_required
def results():
    responses = UserResponse.query.filter_by(user_id=current_user.id).order_by(UserResponse.id.desc()).limit(3).all()
    if not responses:
        flash('No quiz results found. Please take the quiz first.', 'warning')
        return redirect(url_for('quiz'))

    score = sum(1 for r in responses if r.is_correct)
    total_questions = len(responses)

    results_data = []
    valid_options = ['A', 'B', 'C', 'D']
    for r in responses:
        correct_option = r.question.correct_option
        if correct_option in valid_options:
            correct_text = f"{correct_option}. {getattr(r.question, f'option_{correct_option.lower()}')}"
        else:
            correct_text = f"{correct_option} (Invalid option)"
        
        results_data.append({
            'question_id': r.question.id,  # Added this line
            'question_text': r.question.question_text,
            'selected_option': f"{r.selected_option}. {getattr(r.question, f'option_{r.selected_option.lower()}')}",
            'correct_option': correct_text,
            'is_correct': r.is_correct,
            'explanation': r.question.explanation or "No explanation available."
        })

    return render_template('results.html', score=score, total_questions=total_questions, results_data=results_data)

@app.route('/dashboard')
@login_required
def dashboard():
    responses = UserResponse.query.filter_by(user_id=current_user.id).all()
    topic_stats = {}
    for r in responses:
        topic = r.question.topic
        if topic not in topic_stats:
            topic_stats[topic] = {'correct': 0, 'total': 0}
        topic_stats[topic]['total'] += 1
        if r.is_correct:
            topic_stats[topic]['correct'] += 1
    
    for topic in topic_stats:
        topic_stats[topic]['percentage'] = (topic_stats[topic]['correct'] / topic_stats[topic]['total']) * 100
    
    points = current_user.points
    review_questions = ReviewQuestion.query.filter_by(user_id=current_user.id).all()

    return render_template('dashboard.html', topic_stats=topic_stats, points=points, review_questions=review_questions)

# New Routes
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.current_password.data):
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Current password is incorrect.', 'danger')
    return render_template('change_password.html', form=form)

@app.route('/reset_password', methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for('reset_token', token=token, _external=True)
            msg = Message('Password Reset Request', recipients=[user.email])
            msg.body = f'To reset your password, visit this link: {reset_url}\nIf you didn’t request this, ignore this email.'
            mail.send(msg)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('login'))
        else:
            flash('No account found with that email.', 'danger')
    return render_template('reset_request.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    email = verify_reset_token(token)
    if not email:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('request_reset'))
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('No account found with that email.', 'danger')
        return redirect(url_for('request_reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been reset! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/mark_review', methods=['POST'])
@login_required
def mark_review():
    try:
        question_id = request.form.get('question_id')
        if not question_id:
            return jsonify({'status': 'error', 'message': 'No question ID provided'}), 400
        question_id = int(question_id)  # This line fails, triggering ValueError
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'status': 'error', 'message': 'Question not found'}), 404
        existing = ReviewQuestion.query.filter_by(user_id=current_user.id, question_id=question_id).first()
        if not existing:
            review = ReviewQuestion(user_id=current_user.id, question_id=question_id)
            db.session.add(review)
            db.session.commit()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'already_marked'})
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid question ID'}), 400  # Caught here
    except Exception as e:
        app.logger.error(f"Error in mark_review: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error: ' + str(e)}), 500

@app.route('/review')
@login_required
def review():
    review_questions = ReviewQuestion.query.filter_by(user_id=current_user.id).all()
    questions = [rq.question for rq in review_questions]
    return render_template('review.html', questions=questions)


@app.route('/marked_quiz', methods=['GET', 'POST'])
@login_required
def marked_quiz():
    if 'quiz_questions' not in session:
        marked_questions = [rq.question for rq in ReviewQuestion.query.filter_by(user_id=current_user.id).all()]
        if len(marked_questions) < 3:
            flash('Not enough marked questions. Please mark at least 3 questions to practice.', 'warning')
            return redirect(url_for('review'))
        selected_questions = random.sample(marked_questions, 3)
        session['quiz_questions'] = [q.id for q in selected_questions]
        session['current_question'] = 0
        session['score'] = 0

    current_idx = session['current_question']
    if current_idx >= len(session['quiz_questions']):
        score = session['score']
        total = len(session['quiz_questions'])
        session.pop('quiz_questions', None)
        session.pop('current_question', None)
        session.pop('score', None)
        flash(f'Marked questions quiz completed! Your score: {score}/{total}', 'success')
        return redirect(url_for('results'))

    question = Question.query.get(session['quiz_questions'][current_idx])
    form = QuizForm()

    if form.validate_on_submit():
        selected = form.answer.data
        is_correct = (selected == question.correct_option)
        response = UserResponse(
            user_id=current_user.id,
            question_id=question.id,
            selected_option=selected,
            is_correct=is_correct
        )
        db.session.add(response)
        if is_correct:
            current_user.points += 10
            session['score'] += 1
        db.session.commit()
        session['current_question'] += 1
        return redirect(url_for('marked_quiz'))

    return render_template('quiz.html', question=question, form=form, current=current_idx + 1, total=len(session['quiz_questions']))
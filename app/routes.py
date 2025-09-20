# app/routes.py
import os
import time
import random
from random import choice

from flask import (
    render_template, request, redirect, url_for, flash, session, jsonify, current_app
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.exc import IntegrityError
from flask_mail import Message
from openai import OpenAI

from app import db, bcrypt, mail
from app.models import User, Question, UserResponse, ReviewQuestion


# -----------------------------
# Forms
# -----------------------------
class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class QuizForm(FlaskForm):
    answer = RadioField("Answer", choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")], validators=[DataRequired()])
    submit = SubmitField("Next")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Change Password")


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")


# -----------------------------
# Token helpers (use current_app)
# -----------------------------
def generate_reset_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="password-reset-salt")


def verify_reset_token(token: str, expiration: int = 3600):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return serializer.loads(token, salt="password-reset-salt", max_age=expiration)
    except Exception:
        return None


# -----------------------------
# Route registration entrypoint
# -----------------------------
def init_routes(app):
    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            try:
                db.session.add(user)
                db.session.commit()
                flash("Account created successfully!", "success")
                return redirect(url_for("login"))
            except IntegrityError:
                db.session.rollback()
                flash("Username or email already taken. Please choose a different one.", "danger")
        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for("home"))
            flash("Login failed. Check your email and password.", "danger")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("home"))

    @app.route("/quiz", methods=["GET", "POST"])
    @login_required
    def quiz():
        total_time_allowed = 600  # seconds (10 minutes)

        if "quiz_start_time" not in session:
            session["quiz_start_time"] = time.time()

        elapsed = time.time() - session["quiz_start_time"]
        remaining = total_time_allowed - elapsed
        if remaining <= 0:
            flash("Time is up for the quiz!", "warning")
            for key in ("quiz_questions", "current_question", "score", "quiz_start_time"):
                session.pop(key, None)
            return redirect(url_for("results"))

        # Initialize questions once
        topic = request.args.get("topic")
        if "quiz_questions" not in session:
            if topic:
                all_q = Question.query.filter_by(topic=topic).all()
                if len(all_q) < 5:
                    flash(f"Not enough questions in {topic}. Please choose another topic or take a general quiz.", "warning")
                    return redirect(url_for("dashboard"))
                selected = random.sample(all_q, 5)
            else:
                responses = UserResponse.query.filter_by(user_id=current_user.id).all()
                topic_stats = {}
                for r in responses:
                    t = r.question.topic
                    topic_stats.setdefault(t, {"correct": 0, "total": 0})
                    topic_stats[t]["total"] += 1
                    if r.is_correct:
                        topic_stats[t]["correct"] += 1

                all_q = Question.query.all()
                if len(all_q) < 5:
                    flash("Not enough questions available. Please add more questions.", "warning")
                    return redirect(url_for("home"))

                if topic_stats:
                    weakest = min(
                        topic_stats,
                        key=lambda t: topic_stats[t]["correct"] / max(1, topic_stats[t]["total"])
                    )
                    pool = [q for q in all_q if q.topic == weakest]
                    if len(pool) >= 5:
                        selected = random.sample(pool, 5)
                    else:
                        remaining_pool = [q for q in all_q if q not in pool]
                        selected = pool + random.sample(remaining_pool, 5 - len(pool))
                else:
                    selected = random.sample(all_q, 5)

            session["quiz_questions"] = [q.id for q in selected]
            session["current_question"] = 0
            session["score"] = 0

        # End of quiz?
        idx = session["current_question"]
        if idx >= len(session["quiz_questions"]):
            score = session["score"]
            total = len(session["quiz_questions"])
            for key in ("quiz_questions", "current_question", "score", "quiz_start_time"):
                session.pop(key, None)
            flash(f"Quiz completed! Your score: {score}/{total}", "success")
            return redirect(url_for("results"))

        question = Question.query.get(session["quiz_questions"][idx])
        form = QuizForm()

        if form.validate_on_submit():
            selected = form.answer.data
            is_correct = (selected == question.correct_option)
            resp = UserResponse(
                user_id=current_user.id,
                question_id=question.id,
                selected_option=selected,
                is_correct=is_correct
            )
            db.session.add(resp)
            if is_correct:
                current_user.points += 10
                session["score"] += 1
            db.session.commit()
            session["current_question"] += 1
            return redirect(url_for("quiz"))

        return render_template(
            "quiz.html",
            question=question,
            form=form,
            current=idx + 1,
            total=len(session["quiz_questions"]),
            overall_time=int(remaining),
        )

    @app.route("/results")
    @login_required
    def results():
        responses = (
            UserResponse.query.filter_by(user_id=current_user.id)
            .order_by(UserResponse.id.desc())
            .limit(5)
            .all()
        )
        if not responses:
            flash("No quiz results found. Please take the quiz first.", "warning")
            return redirect(url_for("quiz"))

        score = sum(1 for r in responses if r.is_correct)
        total = len(responses)

        marked_ids = {rq.question_id for rq in ReviewQuestion.query.filter_by(user_id=current_user.id).all()}

        valid = ["A", "B", "C", "D"]
        results_data = []
        for r in responses:
            correct = r.question.correct_option
            if correct in valid:
                correct_text = f"{correct}. {getattr(r.question, f'option_{correct.lower()}')}"
            else:
                correct_text = f"{correct} (Invalid option)"

            results_data.append({
                "question_id": r.question.id,
                "question_text": r.question.question_text,
                "selected_option": f"{r.selected_option}. {getattr(r.question, f'option_{r.selected_option.lower()}')}",
                "correct_option": correct_text,
                "is_correct": r.is_correct,
                "is_marked": r.question.id in marked_ids,
            })

        return render_template(
            "results.html",
            score=score,
            total_questions=total,
            results_data=results_data
        )

    @app.route("/dashboard")
    @login_required
    def dashboard():
        responses = UserResponse.query.filter_by(user_id=current_user.id).all()
        topic_stats = {}
        for r in responses:
            t = r.question.topic
            topic_stats.setdefault(t, {"correct": 0, "total": 0})
            topic_stats[t]["total"] += 1
            if r.is_correct:
                topic_stats[t]["correct"] += 1

        for t in topic_stats:
            topic_stats[t]["percentage"] = (
                topic_stats[t]["correct"] / max(1, topic_stats[t]["total"]) * 100
            )

        points = current_user.points
        exam_years = [y for (y,) in db.session.query(Question.exam_year).filter(Question.exam_year.isnot(None)).distinct().all()]
        review_questions = ReviewQuestion.query.filter_by(user_id=current_user.id).all()

        return render_template(
            "dashboard.html",
            topic_stats=topic_stats,
            points=points,
            review_questions=review_questions,
            exam_years=exam_years,
        )

    @app.route("/change_password", methods=["GET", "POST"])
    @login_required
    def change_password():
        form = ChangePasswordForm()
        if form.validate_on_submit():
            if bcrypt.check_password_hash(current_user.password, form.current_password.data):
                current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
                db.session.commit()
                flash("Your password has been updated!", "success")
                return redirect(url_for("dashboard"))
            flash("Current password is incorrect.", "danger")
        return render_template("change_password.html", form=form)

    @app.route("/reset_password", methods=["GET", "POST"])
    def request_reset():
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        form = RequestResetForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                token = generate_reset_token(user.email)
                reset_url = url_for("reset_token", token=token, _external=True)
                msg = Message("Password Reset Request", recipients=[user.email])
                msg.body = f"To reset your password, visit this link: {reset_url}\nIf you didn’t request this, ignore this email."
                mail.send(msg)
                flash("An email has been sent with instructions to reset your password.", "info")
                return redirect(url_for("login"))
            flash("No account found with that email.", "danger")
        return render_template("reset_request.html", form=form)

    @app.route("/reset_password/<token>", methods=["GET", "POST"])
    def reset_token(token):
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        email = verify_reset_token(token)
        if not email:
            flash("The reset link is invalid or has expired.", "danger")
            return redirect(url_for("request_reset"))
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for("request_reset"))

        form = ResetPasswordForm()
        if form.validate_on_submit():
            user.password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            db.session.commit()
            flash("Your password has been reset! Please log in.", "success")
            return redirect(url_for("login"))
        return render_template("reset_password.html", form=form)

    @app.route("/mark_review", methods=["POST"])
    @login_required
    def mark_review():
        try:
            qid = request.form.get("question_id")
            if not qid:
                return jsonify({"status": "error", "message": "No question ID provided"}), 400
            qid = int(qid)
            question = Question.query.get(qid)
            if not question:
                return jsonify({"status": "error", "message": "Question not found"}), 404

            existing = ReviewQuestion.query.filter_by(user_id=current_user.id, question_id=qid).first()
            if not existing:
                db.session.add(ReviewQuestion(user_id=current_user.id, question_id=qid))
                db.session.commit()
                return jsonify({"status": "success"})
            return jsonify({"status": "already_marked"})
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid question ID"}), 400
        except Exception as e:
            current_app.logger.error(f"Error in mark_review: {e}")
            return jsonify({"status": "error", "message": "Server error"}), 500

    @app.route("/review")
    @login_required
    def review():
        review_qs = ReviewQuestion.query.filter_by(user_id=current_user.id).all()
        questions = [rq.question for rq in review_qs]
        return render_template("review.html", questions=questions)

    @app.route("/marked_quiz", methods=["GET", "POST"])
    @login_required
    def marked_quiz():
        if "quiz_questions" not in session:
            marked = [rq.question for rq in ReviewQuestion.query.filter_by(user_id=current_user.id).all()]
            if len(marked) < 5:
                flash("Not enough marked questions. Please mark at least 5 questions to practice.", "warning")
                return redirect(url_for("review"))
            selected = random.sample(marked, 5)
            session["quiz_questions"] = [q.id for q in selected]
            session["current_question"] = 0
            session["score"] = 0

        idx = session["current_question"]
        if idx >= len(session["quiz_questions"]):
            score = session["score"]
            total = len(session["quiz_questions"])
            for key in ("quiz_questions", "current_question", "score"):
                session.pop(key, None)
            flash(f"Marked questions quiz completed! Your score: {score}/{total}", "success")
            return redirect(url_for("results"))

        question = Question.query.get(session["quiz_questions"][idx])
        form = QuizForm()

        if form.validate_on_submit():
            selected = form.answer.data
            is_correct = (selected == question.correct_option)
            db.session.add(UserResponse(
                user_id=current_user.id,
                question_id=question.id,
                selected_option=selected,
                is_correct=is_correct
            ))
            if is_correct:
                current_user.points += 10
                session["score"] += 1
            db.session.commit()
            session["current_question"] += 1
            return redirect(url_for("marked_quiz"))

        return render_template("quiz.html", question=question, form=form, current=idx + 1, total=len(session["quiz_questions"]))

    @app.route("/unmark_review", methods=["POST"])
    @login_required
    def unmark_review():
        try:
            qid = request.form.get("question_id")
            if not qid:
                return jsonify({"status": "error", "message": "No question ID provided"}), 400
            qid = int(qid)
            review = ReviewQuestion.query.filter_by(user_id=current_user.id, question_id=qid).first()
            if review:
                db.session.delete(review)
                db.session.commit()
                return jsonify({"status": "success", "message": "Question unmarked"})
            return jsonify({"status": "error", "message": "Question not marked for review"}), 404
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid question ID"}), 400
        except Exception as e:
            current_app.logger.error(f"Error in unmark_review: {e}")
            return jsonify({"status": "error", "message": "Server error"}), 500

    @app.route("/explain/<int:question_id>", methods=["POST"])
    @login_required
    def explain(question_id):
        question = Question.query.get_or_404(question_id)
        current_app.logger.info(f"Fetching explanation for question {question_id}")
        try:
            explanation = question.explanation if question.explanation else "No explanation available."
            return jsonify({"explanation": explanation})
        except Exception as e:
            current_app.logger.error(f"Error retrieving explanation: {e}")
            return jsonify({"explanation": "Sorry, explanation unavailable."}), 500

    @app.route("/ai_feedback", methods=["POST"])
    @login_required
    def ai_feedback():
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            current_app.logger.error("OpenAI API key not set")
            return jsonify({"feedback": "AI feedback unavailable due to configuration error."}), 500

        client = OpenAI(api_key=api_key)

        responses = UserResponse.query.filter_by(user_id=current_user.id).all()
        topic_stats = {}
        for r in responses:
            t = r.question.topic
            topic_stats.setdefault(t, {"correct": 0, "total": 0})
            topic_stats[t]["total"] += 1
            if r.is_correct:
                topic_stats[t]["correct"] += 1

        for t in topic_stats:
            s = topic_stats[t]
            s["percentage"] = (s["correct"] / max(1, s["total"])) * 100

        prompt = (
            "Based on the following topic statistics, provide concise feedback and study "
            "recommendations in LaTeX-friendly format (use \\( \\) for equations):\n"
            + "\n".join(f"- {t}: {s['correct']}/{s['total']} ({s['percentage']:.1f}%)" for t, s in topic_stats.items())
        )

        try:
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful math tutor. Keep feedback concise and use LaTeX where appropriate."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.7,
            )
            feedback = resp.choices[0].message.content.strip()
            return jsonify({"feedback": feedback})
        except Exception as e:
            current_app.logger.error(f"OpenAI API error: {e}")
            return jsonify({"feedback": "Sorry, I couldn't generate feedback right now."}), 500

    @app.route("/test_openai")
    @login_required
    def test_openai():
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY not set."
        client = OpenAI(api_key=api_key)
        try:
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say hello!"}],
                max_tokens=10,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    @app.route("/jamb")
    @login_required
    def jamb_practice():
        jamb_q = Question.query.filter(Question.exam_year.ilike("%jamb%")).all()
        if len(jamb_q) < 5:
            flash("Not enough JAMB questions available.", "warning")
            return redirect(url_for("dashboard"))
        selected = random.sample(jamb_q, 5)
        session["quiz_questions"] = [q.id for q in selected]
        session["current_question"] = 0
        session["score"] = 0
        session.pop("quiz_start_time", None)
        flash("JAMB practice quiz started!", "info")
        return redirect(url_for("quiz"))

    @app.route("/filter")
    @login_required
    def filter_questions():
        selected_year = request.args.get("year")
        if selected_year:
            filtered = Question.query.filter(Question.exam_year.ilike(f"%{selected_year}%")).all()
        else:
            filtered = Question.query.all()

        if len(filtered) < 5:
            flash("Not enough questions available for the selected filter.", "warning")
            return redirect(url_for("dashboard"))

        selected = random.sample(filtered, 5)
        session["quiz_questions"] = [q.id for q in selected]
        session["current_question"] = 0
        session["score"] = 0
        session.pop("quiz_start_time", None)

        flash(f"Quiz filtered by exam year '{selected_year}' started!", "info")
        return redirect(url_for("quiz"))

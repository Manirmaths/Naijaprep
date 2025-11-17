import os
import time
import random

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
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from flask_mail import Message
from openai import OpenAI

from app import db, bcrypt, mail
from app.models import User, Question, UserResponse, ReviewQuestion
from app.subjects import SUBJECTS 
from app.__init__ import limiter
from sqlalchemy import func, case

from io import StringIO
import csv
from flask import make_response

#SUBJECTS = [
#    "Mathematics", "English", "Physics", "Chemistry", "Biology",
 #   "Geography", "Economics", "Literature", "Government",
#    "Commerce", "Accounting"
#]

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
    
    @limiter.limit("3 per minute")
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
    
    @limiter.limit("5 per minute")
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

    # ------------------ SUBJECTS ------------------
    @app.route("/subjects")
    @login_required
    def subjects():
        # Initialize counts for all known subjects
        counts = {s: 0 for s in SUBJECTS}

        # One grouped query to count per subject
        rows = (
            db.session.query(Question.subject, func.count(Question.id))
            .filter(Question.subject.in_(SUBJECTS))
            .group_by(Question.subject)
            .all()
        )
        for sub, cnt in rows:
            counts[sub] = cnt

        return render_template("subjects.html", subjects=SUBJECTS, subject_counts=counts)


    @app.route("/subjects/<subject>")
    @login_required
    def subject_topics(subject):
        if subject not in SUBJECTS:
            flash("Unknown subject.", "warning")
            return redirect(url_for("subjects"))

        # Distinct topics + counts inside the subject
        rows = (
            db.session.query(Question.topic, func.count(Question.id))
            .filter(Question.subject == subject)
            .group_by(Question.topic)
            .order_by(Question.topic.asc())
            .all()
        )
        topics = [{"name": t, "count": c} for (t, c) in rows]
        if not topics:
            flash(f"No topics found in {subject}.", "warning")
        return render_template("subject_topics.html", subject=subject, topics=topics)

 # ------------------ QUIZ ------------------
# ------------------ QUIZ ------------------
    @app.route("/quiz", methods=["GET", "POST"])
    @login_required
    def quiz():
        """
        Params (GET):
        - subject: optional subject name
        - topic: optional topic name
        - n: desired number of questions (default 5, clamp [3, 50])
        - difficulty: optional integer or 'any'
        - per_q: optional per-question time limit in seconds (e.g., 40). If omitted, disabled.

        Behavior:
        - Excludes user's most recent 50 answered questions to reduce repeats.
        - If not enough questions at requested difficulty, relax to 'any'.
        - Persists exact question ids to session["last_quiz_ids"] for /results.
        - If per_q is enabled, shows a countdown and auto-submits when time hits 0.
            Auto-submission records the question as incorrect without a selection.
        """
        TOTAL_TIME_ALLOWED = 600  # seconds overall

        # ---- read filters ----
        subject = request.args.get("subject", type=str)
        topic = request.args.get("topic", type=str)
        n = request.args.get("n", default=5, type=int)
        difficulty_raw = request.args.get("difficulty", default="any")
        per_q_arg = request.args.get("per_q", type=int)  # may be None

        # sanitize n
        try:
            n = max(3, min(int(n), 50))
        except Exception:
            n = 5

        # normalize difficulty
        if isinstance(difficulty_raw, str) and difficulty_raw.lower() == "any":
            difficulty = None
        else:
            try:
                difficulty = int(difficulty_raw)
            except Exception:
                difficulty = None

        # normalize per_q (store in session so we keep it while paging)
        if per_q_arg is not None:
            # clamp to a sensible range, e.g. 15..180 seconds
            per_q = max(15, min(int(per_q_arg), 180))
            session["per_q"] = per_q
        per_q = session.get("per_q")  # None if not set

        # ---- require a choice when starting fresh ----
        if "quiz_questions" not in session and not topic and not subject:
            flash("Choose a subject to begin your quiz.", "info")
            return redirect(url_for("subjects"))

        # ---- global timer ----
        if "quiz_start_time" not in session:
            session["quiz_start_time"] = time.time()

        elapsed = time.time() - session["quiz_start_time"]
        remaining_overall = TOTAL_TIME_ALLOWED - elapsed
        if remaining_overall <= 0:
            # Time up: preserve current quiz for /results.
            if "quiz_questions" in session:
                session["last_quiz_ids"] = list(session["quiz_questions"])
            session["last_quiz_params"] = {
                "subject": subject,
                "topic": topic,
                "n": n,
                "difficulty": difficulty if difficulty is not None else "any",
                "per_q": per_q,
                "reason": "timeout",
            }
            flash("Time is up for the quiz!", "warning")
            for key in ("quiz_questions", "current_question", "score", "quiz_start_time", "q_start_time"):
                session.pop(key, None)
            return redirect(url_for("results"))

        # ---- initialize question list once ----
        if "quiz_questions" not in session:
            q = Question.query
            src_label = "all subjects"
            if topic:
                q = q.filter(Question.topic == topic)
                src_label = f"topic '{topic}'"
            elif subject:
                q = q.filter(Question.subject == subject)
                src_label = f"subject '{subject}'"

            if difficulty is not None:
                q = q.filter(Question.difficulty == difficulty)

            # avoid recent repeats
            recent_ids = [
                qid for (qid,) in (
                    db.session.query(UserResponse.question_id)
                    .filter(UserResponse.user_id == current_user.id)
                    .order_by(UserResponse.id.desc())
                    .limit(50)
                    .all()
                )
            ]
            if recent_ids:
                q = q.filter(~Question.id.in_(recent_ids))

            pool = q.all()

            # relax difficulty if too small
            if len(pool) < n and difficulty is not None:
                q_relaxed = Question.query
                if topic:
                    q_relaxed = q_relaxed.filter(Question.topic == topic)
                elif subject:
                    q_relaxed = q_relaxed.filter(Question.subject == subject)
                if recent_ids:
                    q_relaxed = q_relaxed.filter(~Question.id.in_(recent_ids))
                pool = q_relaxed.all()

            if len(pool) < n:
                flash(f"Not enough questions in {src_label} for your selection.", "warning")
                if subject:
                    return redirect(url_for("subject_topics", subject=subject))
                return redirect(url_for("subjects"))

            selected = random.sample(pool, n)
            session["quiz_questions"] = [q.id for q in selected]
            session["current_question"] = 0
            session["score"] = 0
            # start the first per-question timer window if enabled
            session.pop("q_start_time", None)

        # ---- end of quiz? ----
        idx = session["current_question"]
        if idx >= len(session["quiz_questions"]):
            score = session["score"]
            total = len(session["quiz_questions"])

            session["last_quiz_ids"] = list(session["quiz_questions"])
            session["last_quiz_params"] = {
                "subject": subject,
                "topic": topic,
                "n": total,
                "difficulty": difficulty if difficulty is not None else "any",
                "per_q": per_q,
                "reason": "completed",
            }

            for key in ("quiz_questions", "current_question", "score", "quiz_start_time", "q_start_time"):
                session.pop(key, None)

            flash(f"Quiz completed! Your score: {score}/{total}", "success")
            return redirect(url_for("results"))

        # ---- current question ----
        question_id = session["quiz_questions"][idx]
        question = Question.query.get(question_id)
        form = QuizForm()

        # Per-question timing window
        now = time.time()
        if per_q:
            if "q_start_time" not in session:
                session["q_start_time"] = now
            perq_elapsed = now - session["q_start_time"]
            perq_remaining = max(0, int(per_q - perq_elapsed))
            # If somehow we render late, still allow client to auto-submit; don't skip here.
        else:
            perq_remaining = None

        # Handle auto-timeout POSTs (no selection). The client sets a flag 'auto_timeout=1'.
        if request.method == "POST" and per_q and request.form.get("auto_timeout") == "1":
            # Record as incorrect without a selection
            db.session.add(UserResponse(
                user_id=current_user.id,
                question_id=question.id,
                selected_option="",   # no selection
                is_correct=False
            ))
            db.session.commit()
            session["current_question"] += 1
            # next question: reset per-question window
            session["q_start_time"] = time.time()

            params = {}
            if topic: params["topic"] = topic
            if subject: params["subject"] = subject
            params["n"] = n
            params["difficulty"] = difficulty if difficulty is not None else "any"
            if per_q: params["per_q"] = per_q
            return redirect(url_for("quiz", **params))

        # Normal submit path
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
            # next question: reset per-question window
            if per_q:
                session["q_start_time"] = time.time()

            # Preserve filters while paging
            params = {}
            if topic: params["topic"] = topic
            if subject: params["subject"] = subject
            params["n"] = n
            params["difficulty"] = difficulty if difficulty is not None else "any"
            if per_q: params["per_q"] = per_q
            return redirect(url_for("quiz", **params))

        return render_template(
            "quiz.html",
            question=question,
            form=form,
            current=idx + 1,
            total=len(session["quiz_questions"]),
            overall_time=int(remaining_overall),
            per_q_remaining=perq_remaining,  # None if disabled
            per_q_enabled=bool(per_q),
        )




    # ------------------ RESULTS / DASHBOARD ------------------
# ------------------ RESULTS ------------------
    @app.route("/results")
    @login_required
    def results():
        """
        If session['last_quiz_ids'] exists, render that exact quiz (in order).
        Else, show the user's 10 most recent responses (legacy fallback).
        """
        def format_option(q, opt_letter: str) -> str:
            opt = (opt_letter or "").upper()
            if opt not in {"A", "B", "C", "D"}:
                return f"{opt_letter} (Invalid option)"
            text = getattr(q, f"option_{opt.lower()}", "") or ""
            return f"{opt}. {text}"

        ids = session.get("last_quiz_ids")

        # -------- Fallback path (no saved ids): latest 10 attempts --------
        if not ids:
            responses = (
                UserResponse.query
                .options(joinedload(UserResponse.question))       # preload Question to avoid N+1
                .filter_by(user_id=current_user.id)
                .order_by(UserResponse.id.desc())
                .limit(10)
                .all()
            )
            if not responses:
                flash("No quiz results found. Please take the quiz first.", "warning")
                return redirect(url_for("subjects"))

            marked_ids = {
                rq.question_id for rq in ReviewQuestion.query.filter_by(user_id=current_user.id).all()
            }

            results_data = []
            for r in responses:
                q = r.question
                results_data.append({
                    "question_id": q.id,
                    "question_text": q.question_text,
                    "selected_option": format_option(q, r.selected_option),
                    "correct_option": format_option(q, q.correct_option),
                    "is_correct": r.is_correct,
                    "is_marked": q.id in marked_ids,
                })

            score = sum(1 for r in responses if r.is_correct)
            total = len(responses)
            return render_template("results.html", score=score, total_questions=total, results_data=results_data)

        # -------- Normal path: show the full last quiz --------
        # Subquery to pick the latest response per question_id in that quiz
        subq = (
            db.session.query(func.max(UserResponse.id).label("max_id"))
            .filter(
                UserResponse.user_id == current_user.id,
                UserResponse.question_id.in_(ids)
            )
            .group_by(UserResponse.question_id)
            .subquery()
        )

        responses = (
            UserResponse.query
            .options(joinedload(UserResponse.question))           # preload Question
            .filter(UserResponse.id.in_(db.session.query(subq.c.max_id)))
            .all()
        )

        if not responses:
            flash("No quiz results found. Please take the quiz first.", "warning")
            return redirect(url_for("subjects"))

        # Keep original quiz order
        by_qid = {r.question_id: r for r in responses}
        ordered_responses = [by_qid[qid] for qid in ids if qid in by_qid]

        marked_ids = {
            rq.question_id for rq in ReviewQuestion.query.filter_by(user_id=current_user.id).all()
        }

        results_data = []
        for r in ordered_responses:
            q = r.question
            results_data.append({
                "question_id": q.id,
                "question_text": q.question_text,
                "selected_option": format_option(q, r.selected_option),
                "correct_option": format_option(q, q.correct_option),
                "is_correct": r.is_correct,
                "is_marked": q.id in marked_ids,
            })

        score = sum(1 for r in ordered_responses if r.is_correct)
        total = len(ordered_responses)
        return render_template("results.html", score=score, total_questions=total, results_data=results_data)




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

    # ------------------ ACCOUNT ------------------
    
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

    @limiter.limit("5 per minute")
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
    
    @limiter.limit("5 per minute")
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

    # ------------------ REVIEW ------------------
    @limiter.limit("30 per minute")
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

    @limiter.limit("30 per minute")
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

    # ------------------ AI Feedback (optional) ------------------
    @limiter.limit("60 per hour")
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

    @limiter.limit("20 per hour")
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

    # ------------------ JAMB / Filters ------------------
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

    @app.route("/practice/weak")
    @login_required
    def practice_weak():
        """
        Start a quiz focused on the user's weakest topics within a subject.

        Query params:
        - subject: required subject name (must be in SUBJECTS)
        - k: how many weakest topics to target (default 3)
        - n: number of questions to pull (default 10; clamped to [3, 50])
        - difficulty: integer or 'any' (default 'any')
        Behavior:
        - Computes per-topic accuracy for this user within the subject.
        - Picks bottom-k topics (lowest accuracy), prefers topics with some history.
        - Builds a pool from those topics; falls back to whole subject if too small.
        - Excludes the user's 50 most recent questions (like /quiz).
        - Initializes session["quiz_questions"] and redirects to /quiz.
        """
        subject = request.args.get("subject", type=str)
        if not subject or subject not in SUBJECTS:
            flash("Pick a valid subject to practice weak areas.", "warning")
            return redirect(url_for("subjects"))

        k = request.args.get("k", default=3, type=int)
        n = request.args.get("n", default=10, type=int)
        difficulty_raw = request.args.get("difficulty", default="any")

        # clamp n
        try:
            n = max(3, min(int(n), 50))
        except Exception:
            n = 10

        # normalize difficulty
        if isinstance(difficulty_raw, str) and difficulty_raw.lower() == "any":
            difficulty = None
        else:
            try:
                difficulty = int(difficulty_raw)
            except Exception:
                difficulty = None

        # --- compute per-topic accuracy for this user within the subject ---
        # totals & correct counts using a join
        stats_rows = (
            db.session.query(
                Question.topic.label("topic"),
                func.count(UserResponse.id).label("total"),
                func.sum(case((UserResponse.is_correct == True, 1), else_=0)).label("correct"),
            )
            .join(Question, UserResponse.question_id == Question.id)
            .filter(
                UserResponse.user_id == current_user.id,
                Question.subject == subject,
            )
            .group_by(Question.topic)
            .all()
        )

        # Build {topic: (correct, total, accuracy)}; topics with no history handled later
        topic_stats = {}
        for row in stats_rows:
            total = int(row.total or 0)
            correct = int(row.correct or 0)
            acc = correct / total if total > 0 else 0.0
            topic_stats[row.topic] = (correct, total, acc)

        # If user has no history in this subject, seed by topics with most questions
        if not topic_stats:
            seed_rows = (
                db.session.query(Question.topic, func.count(Question.id))
                .filter(Question.subject == subject)
                .group_by(Question.topic)
                .order_by(func.count(Question.id).desc())
                .all()
            )
            weak_topics = [t for (t, _) in seed_rows][:max(k, 1)]
        else:
            # Sort by (accuracy asc, total desc -> prioritize low accuracy; if tie, larger sample first)
            ordered = sorted(
                topic_stats.items(),
                key=lambda kv: (kv[1][2], -kv[1][1])
            )
            weak_topics = [t for (t, _info) in ordered[:max(k, 1)]]

        if not weak_topics:
            flash(f"No topics found in {subject}.", "warning")
            return redirect(url_for("subject_topics", subject=subject))

        # --- build pool from weak topics (optionally filter difficulty) ---
        q = Question.query.filter(
            Question.subject == subject,
            Question.topic.in_(weak_topics)
        )
        if difficulty is not None:
            q = q.filter(Question.difficulty == difficulty)

        # Exclude most recent 50 questions this user answered
        recent_ids = (
            db.session.query(UserResponse.question_id)
            .filter(UserResponse.user_id == current_user.id)
            .order_by(UserResponse.id.desc())
            .limit(50)
            .all()
        )
        recent_ids = [qid for (qid,) in recent_ids]
        if recent_ids:
            q = q.filter(~Question.id.in_(recent_ids))

        pool = q.all()

        # Fallback: if pool too small, relax to whole subject (same difficulty / repeats-exclusion)
        if len(pool) < n:
            q_relaxed = Question.query.filter(Question.subject == subject)
            if difficulty is not None:
                q_relaxed = q_relaxed.filter(Question.difficulty == difficulty)
            if recent_ids:
                q_relaxed = q_relaxed.filter(~Question.id.in_(recent_ids))
            pool = q_relaxed.all()

        if len(pool) < n:
            # Final fallback: if still too small, just use whatever exists (could be < n)
            if not pool:
                flash(f"Not enough questions in {subject} to start weak-areas practice.", "warning")
                return redirect(url_for("subject_topics", subject=subject))
            n = min(n, len(pool))

        selected = random.sample(pool, n)
        session["quiz_questions"] = [q.id for q in selected]
        session["current_question"] = 0
        session["score"] = 0
        # fresh overall timer for this focused session
        session.pop("quiz_start_time", None)

        flash(f"Practicing weak areas in {subject} (topics: {', '.join(weak_topics)})", "info")
        # Hand off to /quiz to render; do NOT pass params so /quiz won't reinitialize
        return redirect(url_for("quiz"))

# --- WRONG-ONLY RETAKE + EXPORT ---

    def _latest_responses_for_ids(user_id, qids):
        """Return latest UserResponse per question_id in the given list, for this user."""
        if not qids:
            return []

        subq = (
            db.session.query(func.max(UserResponse.id).label("max_id"))
            .filter(UserResponse.user_id == user_id, UserResponse.question_id.in_(qids))
            .group_by(UserResponse.question_id)
            .subquery()
        )
        return (
            UserResponse.query
            .options(joinedload(UserResponse.question))
            .filter(UserResponse.id.in_(db.session.query(subq.c.max_id)))
            .all()
        )

    @app.route("/retake_wrong", methods=["POST"])
    @login_required
    # If you wired Flask-Limiter earlier, keep this. Otherwise remove the decorator.
    # @limiter.limit("10 per minute")
    def retake_wrong():
        """
        Start a new quiz using only the questions the user got wrong in the last quiz.
        Falls back with a flash if there are fewer than 3 wrong questions.
        """
        ids = session.get("last_quiz_ids")
        if not ids:
            flash("No recent quiz to retake. Take a quiz first.", "warning")
            return redirect(url_for("subjects"))

        responses = _latest_responses_for_ids(current_user.id, ids)
        wrong_qids = [r.question_id for r in responses if not r.is_correct]

        if len(wrong_qids) < 3:
            flash("Not enough wrong questions to retake (need at least 3).", "info")
            return redirect(url_for("results"))

        # Initialize a new quiz session with exactly these wrong questions (randomize order).
        random.shuffle(wrong_qids)
        session["quiz_questions"] = wrong_qids
        session["current_question"] = 0
        session["score"] = 0
        # Reset the global timer
        session.pop("quiz_start_time", None)

        flash(f"Retake started with {len(wrong_qids)} missed question(s). Good luck!", "info")
        return redirect(url_for("quiz"))

    @app.route("/export_wrong_csv", methods=["POST"])
    @login_required
    # @limiter.limit("5 per minute")
    def export_wrong_csv():
        """
        Download a CSV of the user's wrong answers from the last quiz,
        including the correct answer and explanation.
        """
        ids = session.get("last_quiz_ids")
        if not ids:
            flash("No recent quiz to export.", "warning")
            return redirect(url_for("subjects"))

        responses = _latest_responses_for_ids(current_user.id, ids)
        wrong = [r for r in responses if not r.is_correct]

        if not wrong:
            flash("Great! No mistakes to export.", "success")
            return redirect(url_for("results"))

        # Build CSV in-memory
        sio = StringIO()
        writer = csv.writer(sio)
        writer.writerow([
            "question_id", "subject", "topic", "exam_year",
            "question_text",
            "option_a", "option_b", "option_c", "option_d",
            "your_answer", "correct_answer", "explanation"
        ])
        for r in wrong:
            q = r.question
            # safe getters
            def opt(letter): return getattr(q, f"option_{letter.lower()}", "") or ""
            writer.writerow([
                q.id, q.subject or "", q.topic or "", q.exam_year or "",
                (q.question_text or "").replace("\n", " ").strip(),
                opt("A"), opt("B"), opt("C"), opt("D"),
                r.selected_option or "",
                q.correct_option or "",
                (q.explanation or "").replace("\n", " ").strip(),
            ])

        output = make_response(sio.getvalue())
        output.headers["Content-Type"] = "text/csv; charset=utf-8"
        output.headers["Content-Disposition"] = "attachment; filename=naijaprep_mistakes.csv"
        return output

import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Question, QuizAttempt, UserResponse, ReviewQuestion, User, QuestionMastery
from app.schemas import (
    QuizStartIn, QuizAttemptOut, QuestionPublic, AnswerIn, AnswerOut, ResultsOut, ResultItem,
)
from app.subjects import SUBJECTS

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

RECENT_EXCLUDE_LIMIT = 50

# Onboarding diagnostic: a short, broad sample across every subject so a
# brand-new user's Dashboard has real topic_stats *and* a projected score
# immediately, rather than waiting for them to stumble into enough regular
# practice on their own. 11 subjects x 3 = 33 answers, comfortably over
# dashboard.py's SCORE_ESTIMATE_MIN_ANSWERS (30) -- finishing the diagnostic
# unlocks the projected-score card in the same sitting.
DIAGNOSTIC_QUESTIONS_PER_SUBJECT = 3

# Practice-quiz pacing: give the student roughly a minute per question, with
# a floor so short quizzes still get a sane amount of time. (JAMB's own CBT
# is closer to ~40s/question under exam pressure -- this is deliberately
# more generous since it's untimed *practice*, not the real thing.)
SECONDS_PER_QUESTION = 60
MIN_TIME_LIMIT_SECONDS = 180


def _time_limit_for(n: int) -> int:
    return max(MIN_TIME_LIMIT_SECONDS, n * SECONDS_PER_QUESTION)


def _pick_pool(db: Session, user_id: int, subject: str | None, topic: str | None, difficulty: str | None, year: str | None = None):
    recent_ids = [
        qid for (qid,) in (
            db.query(UserResponse.question_id)
            .filter(UserResponse.user_id == user_id)
            .order_by(UserResponse.id.desc())
            .limit(RECENT_EXCLUDE_LIMIT)
            .all()
        )
    ]

    def build(with_difficulty: bool):
        q = db.query(Question).filter(Question.status == "active")
        if topic:
            q = q.filter(Question.topic == topic)
        elif subject:
            q = q.filter(Question.subject == subject)
        if year:
            q = q.filter(Question.year == year)
        if with_difficulty and difficulty is not None:
            q = q.filter(Question.difficulty == difficulty)
        if recent_ids:
            q = q.filter(~Question.id.in_(recent_ids))
        return q.all()

    pool = build(with_difficulty=True)
    return pool, build


def _question_public(q: Question) -> QuestionPublic:
    from app.schemas import PassageOut
    return QuestionPublic(
        id=q.id, question_id=q.question_id, subject=q.subject, topic=q.topic,
        subtopic=q.subtopic, difficulty=q.difficulty,
        question_text=q.question_text, image_url=q.image_url,
        option_a=q.option_a, option_b=q.option_b,
        option_c=q.option_c, option_d=q.option_d, year=q.year,
        passage=PassageOut.model_validate(q.passage) if q.passage else None,
    )


def _attempt_out(db: Session, attempt: QuizAttempt) -> QuizAttemptOut:
    finished = attempt.finished_at is not None or attempt.current_index >= len(attempt.question_ids)
    current_q = None
    if not finished:
        qid = attempt.question_ids[attempt.current_index]
        q = db.get(Question, qid)
        current_q = _question_public(q) if q else None
    return QuizAttemptOut(
        attempt_id=attempt.id,
        mode=attempt.mode,
        total=len(attempt.question_ids),
        current_index=attempt.current_index,
        time_limit_seconds=attempt.time_limit_seconds,
        per_question_seconds=attempt.per_question_seconds,
        current_question=current_q,
        finished=finished,
        score=attempt.score,
    )


@router.post("/start", response_model=QuizAttemptOut)
def start_quiz(payload: QuizStartIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    n = max(3, min(payload.n, 50))
    pool, build = _pick_pool(db, user.id, payload.subject, payload.topic, payload.difficulty, payload.year)

    if len(pool) < n and payload.difficulty is not None:
        pool = build(with_difficulty=False)

    if len(pool) < n:
        label = f"topic '{payload.topic}'" if payload.topic else (
            f"subject '{payload.subject}'" if payload.subject else "all subjects"
        )
        if payload.year:
            label += f" for {payload.year}"
        raise HTTPException(status_code=400, detail=f"Not enough questions in {label} for your selection.")

    selected = random.sample(pool, n)
    per_q = None
    if payload.per_q:
        per_q = max(15, min(payload.per_q, 180))

    attempt = QuizAttempt(
        user_id=user.id,
        mode="quiz",
        subject=payload.subject,
        topic=payload.topic,
        question_ids=[q.id for q in selected],
        current_index=0,
        score=0,
        time_limit_seconds=_time_limit_for(n),
        per_question_seconds=per_q,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return _attempt_out(db, attempt)


@router.post("/start-diagnostic", response_model=QuizAttemptOut)
def start_diagnostic(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.has_taken_diagnostic:
        raise HTTPException(status_code=400, detail="You've already taken the diagnostic.")

    question_ids: list[int] = []
    for subject in SUBJECTS:
        pool = (
            db.query(Question.id)
            .filter(Question.status == "active", Question.subject == subject)
            .all()
        )
        pool = [qid for (qid,) in pool]
        if not pool:
            continue
        n = min(DIAGNOSTIC_QUESTIONS_PER_SUBJECT, len(pool))
        question_ids.extend(random.sample(pool, n))

    if len(question_ids) < 10:
        # Should only happen on a near-empty dev DB -- a real deployed
        # question bank always clears this easily.
        raise HTTPException(status_code=400, detail="Not enough questions available yet for a diagnostic.")

    random.shuffle(question_ids)
    attempt = QuizAttempt(
        user_id=user.id,
        mode="diagnostic",
        subject=None,
        topic=None,
        question_ids=question_ids,
        current_index=0,
        score=0,
        time_limit_seconds=_time_limit_for(len(question_ids)),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return _attempt_out(db, attempt)


@router.get("/{attempt_id}", response_model=QuizAttemptOut)
def get_attempt(attempt_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    attempt = db.get(QuizAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id:
        raise HTTPException(status_code=404, detail="Quiz attempt not found.")
    return _attempt_out(db, attempt)


@router.post("/{attempt_id}/answer", response_model=AnswerOut)
def answer_quiz(attempt_id: int, payload: AnswerIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    attempt = db.get(QuizAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id:
        raise HTTPException(status_code=404, detail="Quiz attempt not found.")
    if attempt.finished_at or attempt.current_index >= len(attempt.question_ids):
        raise HTTPException(status_code=400, detail="This quiz attempt is already finished.")

    expected_qid = attempt.question_ids[attempt.current_index]
    if payload.question_id != expected_qid:
        raise HTTPException(status_code=400, detail="This isn't the current question for this attempt.")

    question = db.get(Question, expected_qid)
    selected = (payload.selected_option or "").upper()[:1]
    is_correct = bool(selected) and selected == question.correct_option

    db.add(UserResponse(
        user_id=user.id,
        question_id=question.id,
        attempt_id=attempt.id,
        selected_option=selected,
        is_correct=is_correct,
    ))
    if is_correct:
        user.points += 10
        attempt.score += 1
    user.record_practice()

    mastery = (
        db.query(QuestionMastery)
        .filter(QuestionMastery.user_id == user.id, QuestionMastery.question_id == question.id)
        .first()
    )
    if mastery is None:
        mastery = QuestionMastery(user_id=user.id, question_id=question.id)
        db.add(mastery)
    mastery.record_answer(is_correct)

    attempt.current_index += 1
    if attempt.current_index >= len(attempt.question_ids):
        attempt.finished_at = datetime.utcnow()
        if attempt.mode == "diagnostic":
            user.has_taken_diagnostic = True

    db.commit()
    db.refresh(attempt)

    return AnswerOut(
        is_correct=is_correct,
        correct_option=question.correct_option,
        explanation=question.explanation,
        next=_attempt_out(db, attempt),
    )


@router.post("/{attempt_id}/skip", response_model=QuizAttemptOut)
def skip_quiz_question(attempt_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    No-penalty skip: advances past the current question without recording a
    UserResponse, so no points/mastery/streak effects -- the student never
    actually attempted it. quiz_results() already treats a question with no
    response row as unanswered (blank, not wrong), so this needs no special
    handling on the results side. Deliberately doesn't reveal correct_option/
    explanation the way answer_quiz's AnswerOut does -- you skipped it, you
    don't get to see the answer.
    """
    attempt = db.get(QuizAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id:
        raise HTTPException(status_code=404, detail="Quiz attempt not found.")
    if attempt.finished_at or attempt.current_index >= len(attempt.question_ids):
        raise HTTPException(status_code=400, detail="This quiz attempt is already finished.")

    attempt.current_index += 1
    if attempt.current_index >= len(attempt.question_ids):
        attempt.finished_at = datetime.utcnow()
        if attempt.mode == "diagnostic":
            user.has_taken_diagnostic = True

    db.commit()
    db.refresh(attempt)
    return _attempt_out(db, attempt)


@router.post("/{attempt_id}/finish", response_model=QuizAttemptOut)
def finish_quiz(attempt_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Explicit finalize for the client-side countdown timer (Quiz.tsx): when
    time runs out, the session ends even if questions remain unanswered, but
    unlike answer_quiz/skip_quiz_question (which auto-set finished_at once
    current_index reaches the end), nothing else marks an early, incomplete
    attempt as finished. Without this, a timed-out attempt with unanswered
    questions left finished_at null forever even though the student was
    already bounced to the results page.

    A timed-out diagnostic still counts as "taken" -- has_taken_diagnostic
    gates whether the onboarding prompt is shown again, and forcing a student
    to redo the whole diagnostic just because the clock ran out would be
    punitive, not protective.

    Idempotent: safe to call even if the attempt already finished normally
    (e.g. the last answer request and the timeout firing in a near-tie) --
    just returns the current state rather than erroring.
    """
    attempt = db.get(QuizAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id:
        raise HTTPException(status_code=404, detail="Quiz attempt not found.")

    if not attempt.finished_at:
        attempt.finished_at = datetime.utcnow()
        if attempt.mode == "diagnostic":
            user.has_taken_diagnostic = True
        db.commit()
        db.refresh(attempt)

    return _attempt_out(db, attempt)


@router.get("/{attempt_id}/results", response_model=ResultsOut)
def quiz_results(attempt_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    attempt = db.get(QuizAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id:
        raise HTTPException(status_code=404, detail="Quiz attempt not found.")

    # Iterate attempt.question_ids (the true set of questions in this
    # attempt), not just logged UserResponse rows -- a question left
    # unanswered (timeout, or skipped in the Mock exam's free-navigation
    # flow) has no response row at all, and computing total from responses
    # alone would silently shrink the denominator (e.g. "178/179" instead of
    # the correct "178/180"). Unanswered questions are reported with an
    # empty selected_option and is_correct=False, same semantics as an
    # explicit blank answer elsewhere in this file.
    responses_by_qid = {
        r.question_id: r
        for r in db.query(UserResponse).filter(UserResponse.attempt_id == attempt_id).all()
    }
    marked_ids = {
        rq.question_id for rq in db.query(ReviewQuestion).filter(ReviewQuestion.user_id == user.id).all()
    }

    items = []
    correct_count = 0
    for qid in attempt.question_ids:
        q = db.get(Question, qid)
        if not q:
            continue
        r = responses_by_qid.get(qid)
        is_correct = bool(r and r.is_correct)
        if is_correct:
            correct_count += 1
        items.append(ResultItem(
            question_id=q.id,
            question_text=q.question_text,
            image_url=q.image_url,
            selected_option=r.selected_option if r else "",
            correct_option=q.correct_option,
            is_correct=is_correct,
            is_marked=q.id in marked_ids,
            explanation=q.explanation,
        ))

    return ResultsOut(score=correct_count, total=len(items), items=items)


@router.post("/{attempt_id}/retake-wrong", response_model=QuizAttemptOut)
def retake_wrong(attempt_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    attempt = db.get(QuizAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id:
        raise HTTPException(status_code=404, detail="Quiz attempt not found.")

    responses = db.query(UserResponse).filter(UserResponse.attempt_id == attempt_id).all()
    wrong_ids = [r.question_id for r in responses if not r.is_correct]
    if len(wrong_ids) < 3:
        raise HTTPException(status_code=400, detail="Not enough wrong questions to retake (need at least 3).")

    random.shuffle(wrong_ids)
    new_attempt = QuizAttempt(
        user_id=user.id, mode="quiz", subject=attempt.subject, topic=attempt.topic,
        question_ids=wrong_ids, current_index=0, score=0,
        time_limit_seconds=_time_limit_for(len(wrong_ids)),
    )
    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)
    return _attempt_out(db, new_attempt)

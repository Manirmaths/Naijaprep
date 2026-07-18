"""
Shared progress-summary computation (topic stats, weak-topic recommendations,
projected score) -- originally lived inline in routers/dashboard.py. Pulled
out so routers/family.py's read-only child/student summary (Phase 5) can
reuse the exact same scoring logic instead of a second, potentially
diverging implementation of "projected score."
"""
from sqlalchemy.orm import Session

from app.models import UserResponse
from app.schemas import ScoreEstimate, TopicStat

# Minimum total answered questions before we'll show a projected score --
# below this the estimate would swing too wildly on a handful of guesses.
SCORE_ESTIMATE_MIN_ANSWERS = 30
# Shown as a range, not a single number: real UTME scoring isn't literally
# "% correct", and this is only ever based on the student's own practice
# history, so a fixed-point number would overstate how precise this is.
SCORE_ESTIMATE_SPREAD = 20
# A topic needs at least this many attempts before it's recommended --
# otherwise one unlucky guess could flag a topic unfairly.
WEAK_TOPIC_MIN_ATTEMPTS = 3
WEAK_TOPIC_MAX_RESULTS = 3


def compute_progress(db: Session, user_id: int) -> tuple[list[TopicStat], list[TopicStat], ScoreEstimate, int]:
    """Returns (topic_stats, recommended_topics, score_estimate, total_answered)."""
    responses = db.query(UserResponse).filter(UserResponse.user_id == user_id).all()
    stats: dict[str, dict] = {}
    subject_stats: dict[str, dict] = {}
    for r in responses:
        t = r.question.topic
        s = stats.setdefault(t, {"correct": 0, "total": 0, "subject": r.question.subject})
        s["total"] += 1
        if r.is_correct:
            s["correct"] += 1

        subj = r.question.subject
        if subj:
            ss = subject_stats.setdefault(subj, {"correct": 0, "total": 0})
            ss["total"] += 1
            if r.is_correct:
                ss["correct"] += 1

    topic_stats = [
        TopicStat(topic=t, subject=s["subject"], correct=s["correct"], total=s["total"],
                   percentage=round(s["correct"] / max(1, s["total"]) * 100, 1))
        for t, s in stats.items()
    ]

    recommended_topics = sorted(
        (t for t in topic_stats if t.total >= WEAK_TOPIC_MIN_ATTEMPTS),
        key=lambda t: t.percentage,
    )[:WEAK_TOPIC_MAX_RESULTS]

    total_answered = len(responses)
    if total_answered >= SCORE_ESTIMATE_MIN_ANSWERS and subject_stats:
        subject_pcts = [s["correct"] / s["total"] * 100 for s in subject_stats.values()]
        avg_pct = sum(subject_pcts) / len(subject_pcts)
        mid = avg_pct / 100 * 400
        score_estimate = ScoreEstimate(
            available=True,
            projected_low=max(0, round(mid - SCORE_ESTIMATE_SPREAD)),
            projected_high=min(400, round(mid + SCORE_ESTIMATE_SPREAD)),
            based_on_answers=total_answered,
        )
    else:
        remaining = max(0, SCORE_ESTIMATE_MIN_ANSWERS - total_answered)
        score_estimate = ScoreEstimate(
            available=False,
            based_on_answers=total_answered,
            message=(
                f"Answer {remaining} more question{'s' if remaining != 1 else ''} to unlock your projected score."
                if remaining else "Practice a couple more subjects to unlock your projected score."
            ),
        )

    return topic_stats, recommended_topics, score_estimate, total_answered

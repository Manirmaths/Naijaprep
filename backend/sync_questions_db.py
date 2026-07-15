#!/usr/bin/env python3
"""
General-purpose sync: upserts ALL of data/questions.csv into a target
database's "question" table, matched by question_id.

Unlike seed_questions.py (insert-only -- skips any question_id already
present) this UPDATES every content column on existing rows to match the
CSV, and INSERTS any question_id that isn't in the DB yet. Nothing else
(id, user_response/quiz_attempt history, which reference Question.id) is
touched, since question_id is unique and Question.id never changes.

Usage:
    python sync_questions_db.py "<DATABASE_URL>"
    python sync_questions_db.py "<DATABASE_URL>" --dry-run

Examples:
    python sync_questions_db.py "sqlite:///./naijaprep.db"
    python sync_questions_db.py "postgresql://user:pass@host/dbname?sslmode=require"
"""
import csv
import os
import sys

from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seed_questions import sanitize, norm_choice, norm_enum, VALID_DIFFICULTY, VALID_SOURCE, VALID_STATUS
from app.subjects import normalize_subject

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "questions.csv")

COLUMNS = [
    "subject", "topic", "subtopic", "difficulty", "year", "exam_type",
    "question_text", "image_url", "option_a", "option_b", "option_c",
    "option_d", "correct_option", "explanation", "tags", "source", "status",
]


def load_row(row):
    return {
        "subject": normalize_subject(row.get("subject")) or (row.get("subject") or "").strip() or None,
        "topic": sanitize((row.get("topic") or "").strip()),
        "subtopic": sanitize((row.get("subtopic") or "").strip()) or None,
        "difficulty": norm_enum(row.get("difficulty"), VALID_DIFFICULTY, "medium"),
        "year": (row.get("year") or "").strip() or None,
        "exam_type": (row.get("exam_type") or "").strip() or None,
        "question_text": sanitize(row.get("question_text") or ""),
        "image_url": (row.get("image_url") or "").strip() or None,
        "option_a": sanitize(row.get("option_a")),
        "option_b": sanitize(row.get("option_b")),
        "option_c": sanitize(row.get("option_c")),
        "option_d": sanitize(row.get("option_d")),
        "correct_option": norm_choice(row.get("correct_option")),
        "explanation": sanitize(row.get("explanation")),
        "tags": (row.get("tags") or "").strip() or None,
        "source": norm_enum(row.get("source"), VALID_SOURCE, "original"),
        "status": norm_enum(row.get("status"), VALID_STATUS, "active"),
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry_run = "--dry-run" in sys.argv
    if len(args) != 1:
        print('Usage: python sync_questions_db.py "<DATABASE_URL>" [--dry-run]')
        sys.exit(1)
    db_url = args[0]

    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    engine = create_engine(db_url)
    with engine.begin() as conn:
        existing_ids = {qid for (qid,) in conn.execute(text('SELECT question_id FROM "question"')).all()}

        set_clause = ", ".join(f"{c} = :{c}" for c in COLUMNS)
        update_sql = text(f'UPDATE "question" SET {set_clause} WHERE question_id = :question_id')
        insert_cols = ["question_id"] + COLUMNS
        insert_sql = text(
            f'INSERT INTO "question" ({", ".join(insert_cols)}) '
            f'VALUES ({", ".join(":" + c for c in insert_cols)})'
        )

        updated = 0
        inserted = 0
        skipped = 0
        for row in rows:
            qid = (row.get("question_id") or "").strip()
            if not qid:
                skipped += 1
                continue
            values = load_row(row)
            if not values["subject"] or not values["topic"] or not values["question_text"]:
                skipped += 1
                continue
            values["question_id"] = qid

            if dry_run:
                if qid in existing_ids:
                    updated += 1
                else:
                    inserted += 1
                continue

            if qid in existing_ids:
                result = conn.execute(update_sql, values)
                if result.rowcount:
                    updated += result.rowcount
            else:
                conn.execute(insert_sql, values)
                existing_ids.add(qid)
                inserted += 1

        if dry_run:
            conn.rollback()

    mode = "DRY RUN -- " if dry_run else ""
    print(f"{mode}Would update: {updated}" if dry_run else f"Updated: {updated}")
    print(f"{mode}Would insert: {inserted}" if dry_run else f"Inserted: {inserted}")
    print(f"Skipped (missing required field): {skipped}")


if __name__ == "__main__":
    main()

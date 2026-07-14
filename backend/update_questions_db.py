#!/usr/bin/env python3
"""
One-off UPDATE script: pushes the 51 already-patched rows from
data/questions.csv into a target database's "question" table, matched
by question_id. Does NOT touch any other row and does NOT insert new
rows -- companion to patch_questions.py, which already rewrote the CSV.

Usage:
    python update_questions_db.py "<DATABASE_URL>"

Examples:
    python update_questions_db.py "sqlite:///./naijaprep.db"
    python update_questions_db.py "postgresql://user:pass@host/dbname?sslmode=require&channel_binding=require"
"""
import csv
import os
import sys

from sqlalchemy import create_engine, text

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "questions.csv")

# Same 51 IDs patched by patch_questions.py.
QUESTION_IDS = [
    "PHY-0014", "PHY-0032", "PHY-0057", "PHY-0060", "PHY-0061", "PHY-0065",
    "PHY-0073", "PHY-0084", "PHY-0092", "PHY-0098", "PHY-0099", "PHY-0100",
    "PHY-0103",
    "CHM-0005", "CHM-0036", "CHM-0054", "CHM-0066", "CHM-0070", "CHM-0078",
    "CHM-0100", "CHM-0102", "CHM-0110",
    "BIO-0005", "BIO-0010", "BIO-0013", "BIO-0028", "BIO-0055", "BIO-0058",
    "BIO-0059", "BIO-0067", "BIO-0081", "BIO-0110",
    "GEO-0073", "GEO-0074", "GEO-0079", "GEO-0080", "GEO-0081", "GEO-0082",
    "ECO-0047",
    "ACC-0013", "ACC-0014", "ACC-0027", "ACC-0029", "ACC-0030", "ACC-0031",
    "ACC-0050", "ACC-0051", "ACC-0052", "ACC-0053", "ACC-0074", "ACC-0077",
]

UPDATE_COLS = [
    "question_text", "image_url", "option_a", "option_b",
    "option_c", "option_d", "correct_option", "explanation",
]


def main():
    if len(sys.argv) != 2:
        print("Usage: python update_questions_db.py \"<DATABASE_URL>\"")
        sys.exit(1)
    db_url = sys.argv[1]

    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        rows = {r["question_id"]: r for r in csv.DictReader(f)}

    missing = [qid for qid in QUESTION_IDS if qid not in rows]
    if missing:
        print("ERROR: these question_ids are missing from the CSV:", missing)
        sys.exit(1)

    engine = create_engine(db_url)
    set_clause = ", ".join(f"{c} = :{c}" for c in UPDATE_COLS)
    sql = text(f'UPDATE "question" SET {set_clause} WHERE question_id = :question_id')

    updated = 0
    not_found = []
    with engine.begin() as conn:
        # image_url used to be VARCHAR(500); the inline SVG data-URIs used
        # for self-contained diagram questions run well past that, so widen
        # the column first. No-op (and harmless) on SQLite or if already TEXT.
        if engine.dialect.name != "sqlite":
            conn.execute(text('ALTER TABLE "question" ALTER COLUMN image_url TYPE TEXT'))

        for qid in QUESTION_IDS:
            row = rows[qid]
            params = {c: row[c] for c in UPDATE_COLS}
            params["question_id"] = qid
            result = conn.execute(sql, params)
            if result.rowcount == 0:
                not_found.append(qid)
            else:
                updated += result.rowcount

    print(f"Updated {updated} row(s) in the DB.")
    if not_found:
        print("WARNING: these question_ids were not found in this DB (no row updated):", not_found)


if __name__ == "__main__":
    main()

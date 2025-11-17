# app/subjects.py

from typing import Optional

# Canonical list used by the UI (order is intentional)
SUBJECTS = [
    "Mathematics",
    "English",
    "Physics",
    "Chemistry",
    "Biology",
    "Geography",
    "Economics",
    "Literature",
    "Government",
    "Commerce",
    "Accounting",
]

# Common aliases you might see in CSVs or user text → canonical
SUBJECT_ALIASES = {
    "math": "Mathematics",
    "mathematics": "Mathematics",
    "english language": "English",
    "eng": "English",
    "phy": "Physics",
    "che": "Chemistry",
    "bio": "Biology",
    "geo": "Geography",
    "econs": "Economics",
    "lit": "Literature",
    "literature in english": "Literature",
    "govt": "Government",
    "government": "Government",
    "comm": "Commerce",
    "commerce": "Commerce",
    "acct": "Accounting",
    "accounting": "Accounting",
}

# Map file name stems → canonical subject (used in seeding)
SUBJECT_FROM_FILENAME = {
    "mathsQuestions": "Mathematics",
    "englishQuestions": "English",
    "physicsQuestions": "Physics",
    "chemistryQuestions": "Chemistry",
    "biologyQuestions": "Biology",
    "geographyQuestions": "Geography",
    "economicsQuestions": "Economics",
    "literatureQuestions": "Literature",
    "governmentQuestions": "Government",
    "commerceQuestions": "Commerce",
    "accountingQuestions": "Accounting",
}

def normalize_subject(raw: Optional[str], filename_hint: Optional[str] = None) -> Optional[str]:
    """
    Normalize noisy subject strings to a canonical member of SUBJECTS.
    - Trims whitespace and lowercases.
    - Uses SUBJECT_ALIASES and filename hints.
    - Returns None if we still can't resolve.
    """
    if raw:
        s = raw.strip().lower()
        if s in SUBJECT_ALIASES:
            return SUBJECT_ALIASES[s]
        # direct title-case match if already canonical-ish
        for can in SUBJECTS:
            if s == can.lower():
                return can

    # Fallback: infer from filename (e.g., mathsQuestions.csv)
    if filename_hint:
        stem = filename_hint.rsplit(".", 1)[0]  # without .csv
        if stem in SUBJECT_FROM_FILENAME:
            return SUBJECT_FROM_FILENAME[stem]

    return None



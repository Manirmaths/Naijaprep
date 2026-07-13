# Canonical subject list (order is intentional -- drives UI ordering too)
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


def normalize_subject(raw: str | None, filename_hint: str | None = None) -> str | None:
    if raw:
        s = raw.strip().lower()
        if s in SUBJECT_ALIASES:
            return SUBJECT_ALIASES[s]
        for can in SUBJECTS:
            if s == can.lower():
                return can
    if filename_hint:
        stem = filename_hint.rsplit(".", 1)[0]
        if stem in SUBJECT_FROM_FILENAME:
            return SUBJECT_FROM_FILENAME[stem]
    return None

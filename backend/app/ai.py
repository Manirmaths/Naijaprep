"""
Minimal OpenAI helper used by four features: the AI tutor ("explain this
differently" chat, routers/tutor.py), admin auto-tagging suggestions
(routers/admin.py), lesson-note generation, and the lesson-note tutor
(routers/notes.py). Falls back to a friendly placeholder if OPENAI_API_KEY
isn't configured, so every feature stays non-fatal until a key is added --
same pattern as app/email.py's Resend fallback.
"""
import json
import logging

import httpx

from app.config import settings

logger = logging.getLogger("naijaprep.ai")

OPENAI_URL = "https://api.openai.com/v1/chat/completions"

TUTOR_FALLBACK = (
    "The AI tutor isn't set up yet on this server. For now, re-read the explanation "
    "above, or ask your teacher about this question."
)

TAGGING_FALLBACK = {
    "subject": None,
    "topic": None,
    "subtopic": None,
    "difficulty": None,
    "note": "AI auto-tagging isn't set up yet on this server -- fill these in manually.",
}

NOTE_TUTOR_FALLBACK = (
    "The AI tutor isn't set up yet on this server. Re-read the note above, or ask your teacher."
)


def _chat(messages: list[dict], *, json_mode: bool = False, max_tokens: int = 500) -> str | None:
    if not settings.OPENAI_API_KEY:
        return None
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.4,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    try:
        resp = httpx.post(
            OPENAI_URL,
            json=payload,
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except httpx.HTTPError:
        logger.exception("OpenAI request failed")
        return None
    except (KeyError, IndexError, ValueError):
        logger.exception("Unexpected OpenAI response shape")
        return None


def ask_tutor(*, question_text: str, options: dict[str, str], correct_option: str,
              explanation: str | None, user_message: str) -> str:
    system = (
        "You are a patient, encouraging tutor helping a Nigerian secondary school student "
        "preparing for JAMB/WAEC/NECO exams. You've been given one multiple-choice question "
        "they've already answered, its correct option, and the existing explanation. The "
        "student wants it explained a different way. Keep your answer short (under 150 words), "
        "concrete, and use simple language and relatable examples. Don't just repeat the "
        "existing explanation -- rephrase or re-derive it differently."
    )
    options_text = "\n".join(f"{k}. {v}" for k, v in options.items())
    user = (
        f"Question: {question_text}\n\nOptions:\n{options_text}\n\n"
        f"Correct answer: {correct_option}\n"
        f"Existing explanation: {explanation or '(none provided)'}\n\n"
        f"Student's question: {user_message}"
    )
    reply = _chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=400,
    )
    return reply.strip() if reply else TUTOR_FALLBACK


def suggest_tags(*, question_text: str, options: dict[str, str], correct_option: str,
                  subjects: list[str]) -> dict:
    system = (
        "You classify JAMB/WAEC/NECO exam questions for an admin tool. Reply with ONLY a JSON "
        "object with keys: subject (must be exactly one of the provided list), topic (short "
        "phrase, e.g. 'Quadratic Equations'), subtopic (short phrase or null), difficulty "
        "(exactly 'easy', 'medium', or 'hard')."
    )
    options_text = "\n".join(f"{k}. {v}" for k, v in options.items())
    user = (
        f"Allowed subjects: {', '.join(subjects)}\n\n"
        f"Question: {question_text}\n\nOptions:\n{options_text}\n\nCorrect answer: {correct_option}"
    )
    reply = _chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        json_mode=True,
        max_tokens=200,
    )
    if not reply:
        return TAGGING_FALLBACK
    try:
        parsed = json.loads(reply)
    except ValueError:
        logger.warning("AI tag suggestion returned non-JSON: %r", reply)
        return TAGGING_FALLBACK
    return {
        "subject": parsed.get("subject") if parsed.get("subject") in subjects else None,
        "topic": parsed.get("topic") or None,
        "subtopic": parsed.get("subtopic") or None,
        "difficulty": parsed.get("difficulty") if parsed.get("difficulty") in ("easy", "medium", "hard") else None,
        "note": None,
    }


NOTE_GENERATION_FAILED = "AI note generation isn't set up on this server, or the request failed -- write this note manually below."


def generate_lesson_note(*, subject: str, topic: str, sample_questions: list[dict]) -> dict:
    """
    Drafts a full lesson note for one (subject, topic). Grounded in a handful
    of real questions already in the bank for that topic (not just the topic
    name in isolation) so the note's coverage actually matches what's tested,
    rather than the model inventing its own idea of what the topic contains.
    Always returns status="draft" territory -- the caller (routers/admin.py)
    saves this as a draft; nothing here is shown to students until an admin
    reviews and publishes it.
    """
    system = (
        "You are an expert West African secondary school teacher writing a lesson note for "
        "Nigerian students preparing for JAMB/WAEC/NECO. Write clearly and simply, like a "
        "well-organized textbook page -- short paragraphs, plain language, and several worked "
        "examples with full step-by-step solutions. A student who reads this note carefully "
        "should be able to answer JAMB-style questions on this exact topic without outside "
        "help. Use \\( ... \\) delimiters for any inline math or formulas. Do not invent "
        "specific statistics, dates, named cases, or legal/constitutional details you aren't "
        "certain about -- prefer explaining the general principle clearly over a fabricated "
        "specific fact.\n\n"
        "Reply with ONLY a JSON object with keys: title (string), summary (1-2 sentence "
        "overview of what this note covers), glossary (array of up to 5 {term, definition} "
        "objects for this topic's key vocabulary), content_md (the full note body as a single "
        "string, using '## ' for section headings, '**text**' for bold, '- ' for bullet points, "
        "and numbered worked examples like 'Example 1:'), related_topics (array of up to 3 "
        "other topic-name strings, same subject, that a student should naturally study next)."
    )
    if sample_questions:
        examples_text = "\n".join(
            f"- {q['question_text']}" + (f" (subtopic: {q['subtopic']})" if q.get("subtopic") else "")
            for q in sample_questions
        )
    else:
        examples_text = "(no sample questions available -- use your own knowledge of the standard JAMB/WAEC syllabus for this topic.)"
    user = (
        f"Subject: {subject}\nTopic: {topic}\n\n"
        f"Here are real exam questions already in our bank for this topic, so you can see what's "
        f"actually being tested and make sure the note covers it:\n{examples_text}"
    )
    reply = _chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        json_mode=True,
        max_tokens=2200,
    )
    if not reply:
        return {
            "title": topic, "summary": None, "glossary": [], "content_md": NOTE_GENERATION_FAILED,
            "related_topics": [], "ok": False,
        }
    try:
        parsed = json.loads(reply)
    except ValueError:
        logger.warning("Lesson note generation returned non-JSON for %s / %s: %r", subject, topic, reply)
        return {
            "title": topic, "summary": None, "glossary": [], "content_md": NOTE_GENERATION_FAILED,
            "related_topics": [], "ok": False,
        }

    glossary = [
        {"term": str(g.get("term", "")).strip(), "definition": str(g.get("definition", "")).strip()}
        for g in (parsed.get("glossary") or [])
        if isinstance(g, dict) and g.get("term") and g.get("definition")
    ][:5]
    related = [str(t).strip() for t in (parsed.get("related_topics") or []) if str(t).strip()][:3]

    return {
        "title": (parsed.get("title") or topic).strip(),
        "summary": (parsed.get("summary") or "").strip() or None,
        "glossary": glossary,
        "content_md": (parsed.get("content_md") or "").strip() or NOTE_GENERATION_FAILED,
        "related_topics": related,
        "ok": True,
    }


def ask_note_tutor(*, subject: str, topic: str, note_excerpt: str, user_message: str) -> str:
    system = (
        f"You are a patient tutor helping a Nigerian student who is reading a lesson note on "
        f"'{topic}' ({subject}) while preparing for JAMB/WAEC/NECO. Answer their question about "
        f"this topic simply and directly. You have a strict short reply budget -- answer in "
        f"under 75 words, get straight to the point, no preamble like 'Great question'."
    )
    user = f"Lesson note excerpt:\n{note_excerpt[:2000]}\n\nStudent's question: {user_message}"
    reply = _chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=100,
    )
    if not reply:
        return NOTE_TUTOR_FALLBACK
    reply = reply.strip()
    # max_tokens=100 can cut the model off mid-sentence rather than at a
    # clean stopping point -- an ellipsis reads as "intentionally trimmed"
    # instead of "broken", which matters since this is a hard budget the
    # student will hit often (see routers/notes.py's token-cap comment).
    if reply and reply[-1] not in ".!?”\"'":
        reply += "…"
    return reply

"""
Minimal OpenAI helper used by two features: the AI tutor ("explain this
differently" chat, routers/tutor.py) and admin auto-tagging suggestions
(routers/admin.py). Falls back to a friendly placeholder if OPENAI_API_KEY
isn't configured, so both features stay non-fatal until a key is added --
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

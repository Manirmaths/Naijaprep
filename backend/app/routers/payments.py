"""
Paystack subscription payments.

Follows the same "configure now or it no-ops safely" pattern already used
for RESEND_API_KEY/OPENAI_API_KEY/VAPID keys (see app/email.py, app/ai.py,
app/push.py): with no PAYSTACK_SECRET_KEY set, /initialize returns a clear
501 instead of a confusing crash, so the rest of the app keeps working in
any environment that hasn't configured payments yet.

Card details are NEVER handled by this backend -- /initialize only asks
Paystack for a hosted checkout URL and redirects the browser there. Paystack
collects the card, then POSTs a signed webhook back to us on success. This
keeps the app out of PCI-DSS scope entirely, which matters a lot more than
usual here given decode/config already flags this repo has real (mostly
teenage) Nigerian users.

Pricing (PREMIUM_PRICE_KOBO/PREMIUM_DURATION_DAYS in config.py) is a
placeholder -- a real business decision, not something to lock in
permanently on the app's behalf. Override via env before taking real money.
"""
import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Payment, QuizAttempt, User
from app.rate_limit import limiter
from app.schemas import PaymentInitializeOut, PremiumStatusOut

router = APIRouter(prefix="/api/payments", tags=["payments"])
logger = logging.getLogger("naijaprep.payments")

PAYSTACK_INITIALIZE_URL = "https://api.paystack.co/transaction/initialize"
PREMIUM_PLAN = "premium_monthly"


def free_mock_exams_used(db: Session, user_id: int) -> int:
    return (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id, QuizAttempt.mode == "mock")
        .count()
    )


@router.get("/status", response_model=PremiumStatusOut)
def payment_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    used = free_mock_exams_used(db, user.id)
    return PremiumStatusOut(
        is_premium=user.is_premium,
        premium_until=user.premium_until,
        free_mock_exams_remaining=max(0, settings.FREE_MOCK_EXAMS - used),
    )


@router.post("/initialize", response_model=PaymentInitializeOut)
@limiter.limit("10/minute")
def initialize_payment(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not settings.PAYSTACK_SECRET_KEY:
        raise HTTPException(
            status_code=501,
            detail="Payments aren't configured on this server yet -- PAYSTACK_SECRET_KEY is unset.",
        )
    if user.is_premium:
        raise HTTPException(status_code=400, detail="You already have an active premium subscription.")

    reference = f"np_{user.id}_{secrets.token_hex(8)}"
    callback_url = f"{settings.PUBLIC_APP_URL.rstrip('/')}/payment-callback"

    try:
        resp = httpx.post(
            PAYSTACK_INITIALIZE_URL,
            json={
                "email": user.email,
                "amount": settings.PREMIUM_PRICE_KOBO,
                "reference": reference,
                "callback_url": callback_url,
                "metadata": {"user_id": user.id, "plan": PREMIUM_PLAN},
            },
            headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()["data"]
    except httpx.HTTPError:
        logger.exception("Paystack initialize failed for user_id=%s", user.id)
        raise HTTPException(status_code=502, detail="Couldn't reach the payment provider. Try again shortly.")

    db.add(Payment(
        user_id=user.id,
        reference=reference,
        plan=PREMIUM_PLAN,
        amount_kobo=settings.PREMIUM_PRICE_KOBO,
        status="pending",
    ))
    db.commit()

    return PaymentInitializeOut(authorization_url=data["authorization_url"], reference=reference)


def _verify_paystack_signature(raw_body: bytes, signature: str | None) -> bool:
    if not signature or not settings.PAYSTACK_SECRET_KEY:
        return False
    expected = hmac.new(settings.PAYSTACK_SECRET_KEY.encode("utf-8"), raw_body, hashlib.sha512).hexdigest()
    # Constant-time comparison -- this is a security boundary (anyone who can
    # forge a valid signature could grant themselves premium for free).
    return hmac.compare_digest(expected, signature)


@router.post("/webhook", status_code=200)
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()
    signature = request.headers.get("x-paystack-signature")

    if not _verify_paystack_signature(raw_body, signature):
        # Deliberately vague + 401, not 400 -- don't help an attacker learn
        # whether it was a missing/malformed/wrong signature.
        raise HTTPException(status_code=401, detail="Invalid signature.")

    payload = await request.json()
    event = payload.get("event")
    if event != "charge.success":
        return {"status": "ignored"}

    data = payload.get("data", {})
    reference = data.get("reference")
    if not reference:
        return {"status": "ignored"}

    payment = db.query(Payment).filter(Payment.reference == reference).first()
    if not payment:
        logger.warning("Paystack webhook for unknown reference=%s", reference)
        return {"status": "ignored"}

    if payment.status == "success":
        return {"status": "already processed"}  # idempotent -- Paystack retries webhooks

    if data.get("status") != "success":
        payment.status = "failed"
        db.commit()
        return {"status": "recorded"}

    payment.status = "success"
    payment.verified_at = datetime.utcnow()

    user = db.get(User, payment.user_id)
    if user:
        # Stack onto existing time left, if any, rather than always resetting
        # to now + duration -- a renewal before expiry shouldn't lose days.
        base = user.premium_until if (user.premium_until and user.premium_until > datetime.utcnow()) else datetime.utcnow()
        user.premium_until = base + timedelta(days=settings.PREMIUM_DURATION_DAYS)

    db.commit()
    return {"status": "processed"}

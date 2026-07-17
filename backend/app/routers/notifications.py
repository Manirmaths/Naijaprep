from datetime import date

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import PushSubscription, User
from app.push import send_push
from app.schemas import PushSubscribeIn, PushUnsubscribeIn, SendRemindersOut, VapidPublicKeyOut

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/vapid-public-key", response_model=VapidPublicKeyOut)
def vapid_public_key():
    # Public by design -- a VAPID public key is meant to be exposed to the
    # browser so it can call PushManager.subscribe({applicationServerKey}).
    return VapidPublicKeyOut(public_key=settings.VAPID_PUBLIC_KEY, configured=bool(settings.VAPID_PRIVATE_KEY))


@router.post("/subscribe", status_code=204)
def subscribe(payload: PushSubscribeIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == payload.endpoint).first()
    if existing:
        existing.user_id = user.id
        existing.p256dh = payload.keys.p256dh
        existing.auth = payload.keys.auth
    else:
        db.add(PushSubscription(
            user_id=user.id, endpoint=payload.endpoint,
            p256dh=payload.keys.p256dh, auth=payload.keys.auth,
        ))
    db.commit()


@router.post("/unsubscribe", status_code=204)
def unsubscribe(payload: PushUnsubscribeIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db.query(PushSubscription).filter(
        PushSubscription.endpoint == payload.endpoint, PushSubscription.user_id == user.id,
    ).delete()
    db.commit()


@router.post("/send-reminders", response_model=SendRemindersOut)
def send_reminders(
    db: Session = Depends(get_db),
    x_cron_secret: str | None = Header(default=None),
):
    """
    Sends a "you haven't practiced today" push to every user with an active
    subscription who hasn't practiced yet today. Not behind normal user auth
    -- meant to be triggered once a day by an external cron (Render's free
    tier has no built-in scheduler), via the X-Cron-Secret header matching
    NOTIFICATIONS_CRON_SECRET.
    """
    if not settings.NOTIFICATIONS_CRON_SECRET or x_cron_secret != settings.NOTIFICATIONS_CRON_SECRET:
        raise HTTPException(status_code=403, detail="Invalid or missing cron secret.")

    today = date.today()
    users_with_subs = (
        db.query(User)
        .join(PushSubscription, PushSubscription.user_id == User.id)
        # last_practice_date is NULL for anyone who's never practiced --
        # "!= today" alone would silently exclude them, since SQL's NULL
        # comparisons evaluate to NULL/unknown rather than true.
        .filter(or_(User.last_practice_date.is_(None), User.last_practice_date != today))
        .distinct()
        .all()
    )

    sent = expired_removed = failed = 0
    for u in users_with_subs:
        subs = db.query(PushSubscription).filter(PushSubscription.user_id == u.id).all()
        for sub in subs:
            result = send_push(
                sub,
                title="Don't break your streak!",
                body=f"You haven't practiced today, {u.username} -- a quick round keeps your streak alive.",
                url="/dashboard",
            )
            if result == "sent":
                sent += 1
            elif result == "expired":
                db.delete(sub)
                expired_removed += 1
            elif result == "failed":
                failed += 1
            # "not_configured" -- silently skip, nothing to clean up.
    db.commit()

    return SendRemindersOut(
        eligible_users=len(users_with_subs), sent=sent, expired_removed=expired_removed, failed=failed,
    )

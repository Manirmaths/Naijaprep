"""
Minimal Web Push helper (used only by routers/notifications.py). Falls back
to a no-op if VAPID keys aren't configured -- same pattern as
app/email.py (Resend) and app/ai.py (OpenAI).
"""
import json
import logging

from pywebpush import webpush, WebPushException

from app.config import settings
from app.models import PushSubscription

logger = logging.getLogger("naijaprep.push")


def send_push(subscription: PushSubscription, title: str, body: str, url: str = "/dashboard") -> str:
    """Returns 'sent', 'expired' (caller should delete the subscription),
    'not_configured', or 'failed'."""
    if not settings.VAPID_PRIVATE_KEY:
        return "not_configured"

    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
            },
            data=json.dumps({"title": title, "body": body, "url": url}),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_CLAIM_EMAIL},
        )
        return "sent"
    except WebPushException as e:
        status = e.response.status_code if e.response is not None else None
        if status in (404, 410):
            # Browser/OS says this subscription no longer exists -- normal
            # churn (uninstall, browser data cleared, etc.), not an error.
            return "expired"
        logger.warning("Push send failed (status=%s): %s", status, e)
        return "failed"

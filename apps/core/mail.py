import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def email_bcc() -> list[str]:
    return list(getattr(settings, "EMAIL_BCC", None) or [])


def send_mail_with_bcc(
    *,
    subject: str,
    message: str,
    recipient_list: list[str],
    from_email: str | None = None,
    fail_silently: bool = False,
) -> int:
    return send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        bcc=email_bcc(),
        fail_silently=fail_silently,
    )

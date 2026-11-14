from django.conf import settings
from django.core.mail import EmailMessage


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
    # django.core.mail.send_mail() has no bcc argument.
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=recipient_list,
        bcc=email_bcc(),
    )
    return email.send(fail_silently=fail_silently)

from __future__ import annotations

from email.mime.image import MIMEImage
from pathlib import Path

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives

LOGO_CID = "logo"
LOGO_FILENAME = "logo-email.png"


def _logo_path() -> Path:
    return Path(settings.BASE_DIR) / "static" / "img" / LOGO_FILENAME


def email_bcc() -> list[str]:
    return list(getattr(settings, "EMAIL_BCC", None) or [])


def absolute_url(path: str) -> str:
    protocol = getattr(settings, "ACCOUNT_DEFAULT_HTTP_PROTOCOL", "http")
    domain = Site.objects.get_current().domain
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{protocol}://{domain}{path}"


def attach_inline_logo(msg: EmailMultiAlternatives) -> None:
    logo_path = _logo_path()
    with logo_path.open("rb") as fp:
        image = MIMEImage(fp.read())
    image.add_header("Content-ID", f"<{LOGO_CID}>")
    image.add_header("Content-Disposition", "inline", filename=LOGO_FILENAME)
    msg.mixed_subtype = "related"
    msg.attach(image)


def send_branded_mail(
    *,
    subject: str,
    template: str,
    context: dict | None = None,
    recipient_list: list[str],
    from_email: str | None = None,
    fail_silently: bool = False,
) -> int:
    from django.template.loader import render_to_string

    render_context = {"site_name": "Sail with Me", **(context or {})}
    text_body = render_to_string(f"{template}.txt", render_context).strip()
    html_body = render_to_string(f"{template}.html", render_context).strip()
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
        bcc=email_bcc(),
    )
    msg.attach_alternative(html_body, "text/html")
    attach_inline_logo(msg)
    return msg.send(fail_silently=fail_silently)

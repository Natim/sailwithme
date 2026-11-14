import logging

from django.utils.translation import gettext as _

from apps.core.mail import send_mail_with_bcc

logger = logging.getLogger(__name__)

MESSAGE_SNIPPET_MAX = 500


def notify_author_of_application(*, author, listing, applicant, message: str, listing_url: str) -> None:
    profile = getattr(applicant, "profile", None)
    applicant_name = profile.public_name() if profile else str(applicant.pk)
    snippet = (message or "").strip()
    if len(snippet) > MESSAGE_SNIPPET_MAX:
        snippet = snippet[: MESSAGE_SNIPPET_MAX - 1] + "…"

    subject = _("Sail with Me — new application for « %(title)s »") % {"title": listing.title}
    body_lines = [
        _("You received a new application on your listing « %(title)s ».") % {"title": listing.title},
        "",
        _("Applicant: %(name)s") % {"name": applicant_name},
    ]
    if snippet:
        body_lines.extend(["", _("Message:"), snippet])
    body_lines.extend(["", _("View the listing: %(url)s") % {"url": listing_url}])
    body = "\n".join(body_lines)

    try:
        send_mail_with_bcc(
            subject=subject,
            message=body,
            recipient_list=[author.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send application notification for listing %s to %s",
            listing.pk,
            author.email,
        )

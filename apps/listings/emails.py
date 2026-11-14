import logging

from django.utils.translation import gettext as _

from apps.core.mail import send_branded_mail

logger = logging.getLogger(__name__)

MESSAGE_SNIPPET_MAX = 500
APPLICATION_TEMPLATE = "emails/listings/application_received"


def notify_author_of_application(*, author, listing, applicant, message: str, listing_url: str) -> None:
    profile = getattr(applicant, "profile", None)
    applicant_name = profile.public_name() if profile else str(applicant.pk)
    snippet = (message or "").strip()
    if len(snippet) > MESSAGE_SNIPPET_MAX:
        snippet = snippet[: MESSAGE_SNIPPET_MAX - 1] + "…"

    subject = _("Sail with Me — new application for « %(title)s »") % {"title": listing.title}
    context = {
        "listing": listing,
        "applicant_name": applicant_name,
        "message_snippet": snippet,
        "listing_url": listing_url,
    }

    try:
        send_branded_mail(
            subject=subject,
            template=APPLICATION_TEMPLATE,
            context=context,
            recipient_list=[author.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send application notification for listing %s to %s",
            listing.pk,
            author.email,
        )

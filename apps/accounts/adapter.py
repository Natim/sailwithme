from allauth.account.adapter import DefaultAccountAdapter
from allauth.core import context as allauth_context
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site


class SailWithMeAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix: str, email: str, context: dict) -> None:
        request = allauth_context.request
        ctx = {
            "request": request,
            "email": email,
            "current_site": get_current_site(request),
        }
        ctx.update(context)
        msg = self.render_mail(template_prefix, email, ctx)
        bcc = getattr(settings, "EMAIL_BCC", None) or []
        if bcc:
            msg.bcc = list(bcc)
        msg.send()

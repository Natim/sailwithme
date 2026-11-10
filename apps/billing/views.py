from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import MembershipPlan
from .services import activate_membership

try:
    import stripe
except ImportError:  # pragma: no cover
    stripe = None


def pricing(request):
    return render(request, "billing/pricing.html")


@login_required
def checkout(request, plan):
    allowed = {c[0] for c in MembershipPlan.choices}
    if plan not in allowed:
        messages.error(request, _("Unknown plan."))
        return redirect("billing:pricing")

    price_map = {
        MembershipPlan.CREW_SEASON: settings.CREW_PASS_SEASON_PRICE_CENTS,
        MembershipPlan.CREW_LIFETIME: settings.CREW_PASS_LIFETIME_PRICE_CENTS,
        MembershipPlan.SKIPPER_PLUS: settings.SKIPPER_PLUS_MONTHLY_PRICE_CENTS,
        MembershipPlan.IDENTITY: settings.IDENTITY_VERIFICATION_PRICE_CENTS,
    }

    if not settings.STRIPE_SECRET_KEY or stripe is None:
        activate_membership(request.user, plan)
        messages.success(request, _("Subscription activated (demo mode without Stripe)."))
        return redirect("billing:success")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    mode = "subscription" if plan == MembershipPlan.SKIPPER_PLUS else "payment"
    session = stripe.checkout.Session.create(
        mode=mode,
        success_url=request.build_absolute_uri("/billing/success/"),
        cancel_url=request.build_absolute_uri("/billing/pricing/"),
        customer_email=request.user.email,
        metadata={"user_id": str(request.user.id), "plan": plan},
        line_items=[
            {
                "price_data": {
                    "currency": "eur",
                    "unit_amount": price_map[plan],
                    "product_data": {"name": dict(MembershipPlan.choices)[plan]},
                    **({"recurring": {"interval": "month"}} if plan == MembershipPlan.SKIPPER_PLUS else {}),
                },
                "quantity": 1,
            }
        ],
    )
    return redirect(session.url)


def checkout_success(request):
    messages.success(request, _("Payment confirmed — thank you!"))
    return render(request, "billing/success.html")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    if not settings.STRIPE_SECRET_KEY or stripe is None:
        return HttpResponse(status=501)

    payload = request.body
    sig = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponseBadRequest()

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        meta = session.get("metadata") or {}
        from apps.accounts.models import User

        user = User.objects.filter(pk=meta.get("user_id")).first()
        if user and meta.get("plan"):
            activate_membership(user, meta["plan"])
    return HttpResponse(status=200)

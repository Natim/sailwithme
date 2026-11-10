from datetime import timedelta

from django.utils import timezone

from apps.profiles.models import ProfileRole

from .models import Membership, MembershipPlan


def user_has_crew_pass(user) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    qs = Membership.objects.filter(user=user, active=True)
    for m in qs:
        if m.plan == MembershipPlan.CREW_LIFETIME and m.active:
            return True
        if m.plan == MembershipPlan.CREW_SEASON and m.is_current():
            return True
    return False


def user_can_initiate_contact(user) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    profile = getattr(user, "profile", None)
    if profile and profile.role == ProfileRole.SKIPPER:
        return True
    return user_has_crew_pass(user)


def user_has_skipper_plus(user) -> bool:
    return Membership.objects.filter(
        user=user,
        plan=MembershipPlan.SKIPPER_PLUS,
        active=True,
    ).exists()


def activate_membership(user, plan: str, season_years: int = 1):
    valid_until = None
    if plan == MembershipPlan.CREW_SEASON:
        valid_until = timezone.now() + timedelta(days=365 * season_years)
    elif plan == MembershipPlan.SKIPPER_PLUS:
        valid_until = timezone.now() + timedelta(days=31)
    Membership.objects.create(
        user=user,
        plan=plan,
        active=True,
        valid_until=valid_until,
    )
    if plan == MembershipPlan.IDENTITY:
        user.identity_verified = True
        user.save(update_fields=["identity_verified"])

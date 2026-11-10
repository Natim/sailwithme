from datetime import timedelta
from typing import Any

from django.utils import timezone
from django.utils.formats import date_format

from apps.profiles.models import ProfileRole

from .models import Membership, MembershipPlan


def membership_summary_for_user(user) -> dict[str, Any]:
    """État lisible des offres pour la page profil."""
    summary: dict[str, Any] = {
        "staff_bypass": False,
        "identity_verified": False,
        "crew_pass_active": False,
        "crew_pass_detail": "",
        "skipper_plus_active": False,
        "skipper_plus_detail": "",
        "can_initiate_contact": False,
    }
    if not user.is_authenticated:
        return summary

    summary["identity_verified"] = bool(getattr(user, "identity_verified", False))
    summary["can_initiate_contact"] = user_can_initiate_contact(user)

    if user.is_staff:
        summary["staff_bypass"] = True
        summary["crew_pass_active"] = True
        summary["crew_pass_detail"] = "Accès staff"
        return summary

    lifetime = (
        Membership.objects.filter(
            user=user,
            plan=MembershipPlan.CREW_LIFETIME,
            active=True,
        )
        .order_by("-created_at")
        .first()
    )
    if lifetime and lifetime.is_current():
        summary["crew_pass_active"] = True
        summary["crew_pass_detail"] = "Crew Pass à vie"

    if not summary["crew_pass_active"]:
        season = (
            Membership.objects.filter(
                user=user,
                plan=MembershipPlan.CREW_SEASON,
                active=True,
            )
            .order_by("-valid_until", "-created_at")
            .first()
        )
        if season and season.is_current():
            summary["crew_pass_active"] = True
            if season.valid_until:
                summary["crew_pass_detail"] = (
                    f"Crew Pass saison — actif jusqu’au {date_format(season.valid_until, 'SHORT_DATE_FORMAT')}"
                )
            else:
                summary["crew_pass_detail"] = "Crew Pass saison"

    skipper = (
        Membership.objects.filter(
            user=user,
            plan=MembershipPlan.SKIPPER_PLUS,
            active=True,
        )
        .order_by("-valid_until", "-created_at")
        .first()
    )
    if skipper and skipper.is_current():
        summary["skipper_plus_active"] = True
        if skipper.valid_until:
            summary["skipper_plus_detail"] = (
                f"Renouvellement prévu le {date_format(skipper.valid_until, 'SHORT_DATE_FORMAT')}"
            )
        else:
            summary["skipper_plus_detail"] = "Abonnement mensuel actif"

    profile = getattr(user, "profile", None)
    if profile and profile.role == ProfileRole.SKIPPER and not summary["crew_pass_active"]:
        summary["crew_pass_detail"] = "Rôle skipper : contact sans Crew Pass"

    return summary


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

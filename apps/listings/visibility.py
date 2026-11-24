from django.db.models import Exists, OuterRef, Q, QuerySet
from django.utils import timezone

from apps.billing.models import Membership, MembershipPlan
from apps.listings.models import Listing, ListingStatus
from apps.profiles.models import ProfileRole


def filter_searchable_listings(qs: QuerySet[Listing]) -> QuerySet[Listing]:
    """Keep published listings whose authors may appear in public search."""
    now = timezone.now()
    lifetime = Membership.objects.filter(
        user_id=OuterRef("author_id"),
        active=True,
        plan=MembershipPlan.CREW_LIFETIME,
    )
    timed_pass = Membership.objects.filter(
        user_id=OuterRef("author_id"),
        active=True,
        plan__in=[MembershipPlan.CREW_SEASON, MembershipPlan.CREW_TRIAL],
    ).filter(Q(valid_until__isnull=True) | Q(valid_until__gte=now))

    return qs.filter(status=ListingStatus.PUBLISHED).filter(
        Q(author__is_staff=True) | Q(author__profile__role=ProfileRole.SKIPPER) | Exists(lifetime) | Exists(timed_pass)
    )

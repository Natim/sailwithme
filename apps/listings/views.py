import json

from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView

from apps.billing.services import user_can_initiate_contact

from .forms import ApplicationForm, ListingForm, ListingSearchForm
from .models import (
    ApplicationStatus,
    Listing,
    ListingApplication,
    ListingKind,
    ListingStatus,
    RoutePage,
    SearchAlert,
    Voyage,
)
from .search import listings_for_map, search_listings


def listing_map_i18n():
    return {
        "hintStart": _("First click: departure · second click: arrival"),
        "hintDeparture": _("Departure set. Click for arrival."),
        "hintEdit": _("Route set. Click the map to change departure, then arrival."),
        "departure": _("Departure"),
        "arrival": _("Arrival"),
    }


def listing_search(request):
    form = ListingSearchForm(request.GET)
    results = []
    map_data = []
    if form.is_valid():
        results = search_listings(form.cleaned_data)
    elif form.is_bound:
        messages.error(request, _("Fix your search criteria."))
    map_data = listings_for_map(results)
    alert_coords = {}
    if form.is_valid():
        cd = form.cleaned_data
        for key in ("departure_lat", "departure_lng", "arrival_lat", "arrival_lng"):
            val = cd.get(key)
            if val is not None:
                alert_coords[key] = val
    ctx = {
        "form": form,
        "results": results,
        "result_count": len(results),
        "map_data_json": json.dumps(map_data),
        "alert_coords": alert_coords,
    }
    return render(request, "listings/search.html", ctx)


class ListingDetailView(DetailView):
    model = Listing
    template_name = "listings/detail.html"
    context_object_name = "listing"

    def get_queryset(self):
        visible = Q(status__in=[ListingStatus.PUBLISHED, ListingStatus.FULL, ListingStatus.EXPIRED])
        if self.request.user.is_authenticated:
            visible |= Q(author=self.request.user)
        return Listing.objects.filter(visible).select_related("author", "author__profile", "boat")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        listing = self.object
        dep = listing.departure_point
        arr = listing.arrival_point
        if dep and arr:
            # PostGIS may expose y/x as Decimal; json_script handles dict + float, not json.dumps(Decimal).
            ctx["listing_route"] = {
                "departure": [float(dep.y), float(dep.x)],
                "arrival": [float(arr.y), float(arr.x)],
            }
        if self.request.user.is_authenticated:
            ctx["application_form"] = ApplicationForm()
        return ctx


class MyListingsView(LoginRequiredMixin, ListView):
    template_name = "listings/mine.html"

    def get_queryset(self):
        return Listing.objects.filter(author=self.request.user).order_by("-created_at")


@login_required
def listing_create(request):
    form = ListingForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        listing = form.save()
        listing.status = ListingStatus.PUBLISHED
        listing.save()
        messages.success(request, _("Listing published."))
        return redirect("listings:detail", pk=listing.pk)
    return render(
        request,
        "listings/form.html",
        {"form": form, "listing": None, "listing_map_i18n": listing_map_i18n()},
    )


@login_required
def listing_edit(request, pk):
    listing = get_object_or_404(Listing, pk=pk, author=request.user)
    form = ListingForm(request.user, request.POST or None, instance=listing)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Listing updated."))
        return redirect("listings:detail", pk=listing.pk)
    return render(
        request,
        "listings/form.html",
        {"form": form, "listing": listing, "listing_map_i18n": listing_map_i18n()},
    )


@login_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk, author=request.user)
    has_applications = listing.applications.exists()
    if request.method == "POST":
        if has_applications:
            listing.status = ListingStatus.WITHDRAWN
            listing.save(update_fields=["status", "updated_at"])
            messages.success(request, _("Listing withdrawn (applications exist and are kept)."))
        else:
            listing.delete()
            messages.success(request, _("Listing deleted."))
        return redirect("listings:mine")
    return render(
        request,
        "listings/confirm_delete.html",
        {"listing": listing, "has_applications": has_applications},
    )


@login_required
def listing_apply(request, pk):
    listing = get_object_or_404(Listing, pk=pk, status=ListingStatus.PUBLISHED)
    if listing.author_id == request.user.id:
        messages.error(request, _("You cannot apply to your own listing."))
        return redirect("listings:detail", pk=pk)
    if not user_can_initiate_contact(request.user) and listing.kind == ListingKind.CREW_WANTED:
        messages.error(request, _("A Crew Pass is required to apply (see Pricing)."))
        return redirect("billing:pricing")
    form = ApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        app, created = ListingApplication.objects.get_or_create(
            listing=listing,
            applicant=request.user,
            defaults={"message": form.cleaned_data["message"]},
        )
        if not created:
            messages.warning(request, _("You already applied."))
        else:
            messages.success(request, _("Application sent."))
            from apps.messaging.services import start_conversation

            start_conversation(request.user, listing.author, listing=listing, first_message=app.message)
        return redirect("listings:detail", pk=pk)
    return redirect("listings:detail", pk=pk)


@login_required
def application_decide(request, app_id, action):
    application = get_object_or_404(
        ListingApplication,
        pk=app_id,
        listing__author=request.user,
    )
    if action == "accept":
        application.status = ApplicationStatus.ACCEPTED
        application.save()
        with transaction.atomic():
            voyage, _ = Voyage.objects.get_or_create(
                listing=application.listing,
                skipper=application.listing.author,
                defaults={"title": application.listing.title},
            )
            voyage.crew.add(application.applicant)
        messages.success(request, _("Application accepted — voyage created."))
    elif action == "reject":
        application.status = ApplicationStatus.REJECTED
        application.save()
        messages.info(request, _("Application declined."))
    return redirect("listings:detail", pk=application.listing_id)


@login_required
def save_search_alert(request):
    if request.method != "POST":
        return redirect("listings:search")
    if not user_can_initiate_contact(request.user):
        messages.error(request, _("Alerts require a Crew Pass."))
        return redirect("billing:pricing")
    search_form = ListingSearchForm(request.POST)
    if search_form.is_valid():
        cd = search_form.cleaned_data
        SearchAlert.objects.create(
            user=request.user,
            name=request.POST.get("alert_name", "").strip() or "Ma recherche",
            kind=cd.get("kind") or "",
            programme_type=cd.get("programme_type") or "",
            departure_lat=cd.get("departure_lat"),
            departure_lng=cd.get("departure_lng"),
            departure_radius_nm=cd.get("departure_radius_nm") or 150,
            arrival_lat=cd.get("arrival_lat"),
            arrival_lng=cd.get("arrival_lng"),
            arrival_radius_nm=cd.get("arrival_radius_nm") or 150,
            year=cd.get("year"),
            week_from=cd.get("week_from"),
            week_to=cd.get("week_to"),
        )
        messages.success(request, _("Alert saved."))
    else:
        messages.error(request, _("Could not save alert: invalid criteria."))
    query = request.POST.urlencode()
    url = reverse("listings:search")
    if query:
        url = f"{url}?{query}"
    return redirect(url)


class RouteSEOPageView(DetailView):
    model = RoutePage
    template_name = "listings/route_page.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "route_page"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        route = self.object
        qs = Listing.objects.filter(status=ListingStatus.PUBLISHED)
        if route.departure_port_id:
            qs = qs.filter(departure_port=route.departure_port)
        if route.arrival_port_id:
            qs = qs.filter(arrival_port=route.arrival_port)
        ctx["listings"] = qs[:20]
        return ctx


class FAQView(TemplateView):
    template_name = "listings/faq.html"

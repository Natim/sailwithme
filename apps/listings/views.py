import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, TemplateView

from apps.billing.services import user_can_initiate_contact

from .forms import ApplicationForm, ListingForm, ListingSearchForm, SearchAlertForm
from .models import (
    ApplicationStatus,
    Listing,
    ListingApplication,
    ListingKind,
    ListingStatus,
    RoutePage,
    Voyage,
)
from .search import listings_for_map, search_listings


def listing_search(request):
    form = ListingSearchForm(request.GET or None)
    results = []
    map_data = []
    if form.is_valid():
        results = search_listings(form.cleaned_data)
        map_data = listings_for_map(results)
    ctx = {
        "form": form,
        "results": results,
        "map_data_json": json.dumps(map_data),
    }
    if request.headers.get("HX-Request"):
        return render(request, "listings/partials/results.html", ctx)
    return render(request, "listings/search.html", ctx)


class ListingDetailView(DetailView):
    model = Listing
    template_name = "listings/detail.html"
    context_object_name = "listing"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
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
        messages.success(request, "Annonce publiée.")
        return redirect("listings:detail", pk=listing.pk)
    return render(request, "listings/form.html", {"form": form})


@login_required
def listing_apply(request, pk):
    listing = get_object_or_404(Listing, pk=pk, status=ListingStatus.PUBLISHED)
    if listing.author_id == request.user.id:
        messages.error(request, "Vous ne pouvez pas postuler à votre propre annonce.")
        return redirect("listings:detail", pk=pk)
    if not user_can_initiate_contact(request.user) and listing.kind == ListingKind.CREW_WANTED:
        messages.error(request, "Un Crew Pass est requis pour postuler (voir Tarifs).")
        return redirect("billing:pricing")
    form = ApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        app, created = ListingApplication.objects.get_or_create(
            listing=listing,
            applicant=request.user,
            defaults={"message": form.cleaned_data["message"]},
        )
        if not created:
            messages.warning(request, "Vous avez déjà postulé.")
        else:
            messages.success(request, "Candidature envoyée.")
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
        messages.success(request, "Candidature acceptée — voyage créé.")
    elif action == "reject":
        application.status = ApplicationStatus.REJECTED
        application.save()
        messages.info(request, "Candidature refusée.")
    return redirect("listings:detail", pk=application.listing_id)


@login_required
def save_search_alert(request):
    if request.method != "POST":
        return redirect("listings:search")
    if not user_can_initiate_contact(request.user):
        messages.error(request, "Les alertes nécessitent un Crew Pass.")
        return redirect("billing:pricing")
    form = SearchAlertForm(request.POST)
    if form.is_valid():
        alert = form.save(commit=False)
        alert.user = request.user
        alert.save()
        messages.success(request, "Alerte enregistrée.")
    return redirect("listings:search")


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

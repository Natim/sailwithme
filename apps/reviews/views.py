from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.listings.models import Voyage

from .forms import ReviewForm
from .models import Review


def _user_on_voyage(voyage: Voyage, user) -> bool:
    if voyage.skipper_id == user.id:
        return True
    return voyage.crew.filter(pk=user.pk).exists()


@login_required
def write_review(request, voyage_id, subject_id):
    voyage = get_object_or_404(Voyage, pk=voyage_id, reviews_open=True)
    if not _user_on_voyage(voyage, request.user):
        messages.error(request, _("You did not take part in this voyage."))
        return redirect("profiles:detail", pk=subject_id)
    if request.user.id == subject_id:
        messages.error(request, _("You cannot review yourself."))
        return redirect("profiles:detail", pk=subject_id)
    if not _user_on_voyage(voyage, voyage.skipper if subject_id == voyage.skipper_id else None):
        pass
    subject_participant = voyage.skipper_id == subject_id or voyage.crew.filter(pk=subject_id).exists()
    if not subject_participant:
        messages.error(request, _("This person was not on the voyage."))
        return redirect("profiles:detail", pk=subject_id)

    existing = Review.objects.filter(
        voyage=voyage,
        author=request.user,
        subject_id=subject_id,
    ).first()
    if existing:
        messages.info(request, _("You already left a review for this voyage."))
        return redirect("profiles:detail", pk=subject_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.voyage = voyage
            review.author = request.user
            review.subject_id = subject_id
            review.save()
            review.try_publish()
            messages.success(request, _("Thanks for your review."))
            return redirect("profiles:detail", pk=subject_id)
    else:
        form = ReviewForm()
    return render(
        request,
        "reviews/form.html",
        {"form": form, "voyage": voyage, "subject_id": subject_id},
    )


@login_required
def respond_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, subject=request.user)
    if request.method == "POST":
        review.response = request.POST.get("response", "")
        review.save()
        messages.success(request, _("Reply published."))
    return redirect("profiles:detail", pk=request.user.id)

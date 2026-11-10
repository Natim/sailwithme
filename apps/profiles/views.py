from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from apps.accounts.models import User

from .forms import ProfileBasicsForm, ProfileExperienceForm, ProfilePreferencesForm
from .models import Profile


class ProfileDetailView(DetailView):
    model = Profile
    template_name = "profiles/detail.html"
    context_object_name = "profile"

    def get_object(self):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        return get_object_or_404(Profile, user=user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.reviews.models import Review

        reviews = Review.objects.filter(
            subject=self.object.user,
            published_at__isnull=False,
        ).select_related("author", "voyage")
        ctx["reviews"] = reviews
        if reviews:
            ctx["avg_rating"] = sum(r.rating_overall for r in reviews) / len(reviews)
        return ctx


class ProfileDirectoryView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = "profiles/directory.html"
    paginate_by = 24

    def get_queryset(self):
        return Profile.objects.filter(crew_directory_visible=True).select_related("user")


@login_required
def profile_me(request):
    profile = request.user.profile
    return render(
        request,
        "profiles/edit.html",
        {
            "profile": profile,
            "basics_form": ProfileBasicsForm(instance=profile),
            "experience_form": ProfileExperienceForm(instance=profile),
            "preferences_form": ProfilePreferencesForm(instance=profile),
        },
    )


@login_required
def profile_edit_section(request, section):
    profile = request.user.profile
    forms_map = {
        "basics": (ProfileBasicsForm, "profiles/partials/basics_form.html"),
        "experience": (ProfileExperienceForm, "profiles/partials/experience_form.html"),
        "preferences": (ProfilePreferencesForm, "profiles/partials/preferences_form.html"),
    }
    form_class, template = forms_map.get(section, (None, None))
    if not form_class:
        return redirect("profiles:me")

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    template,
                    {"form": form_class(instance=profile), "saved": True},
                )
            return redirect("profiles:me")
    else:
        form = form_class(instance=profile)

    return render(request, template, {"form": form, "saved": False})

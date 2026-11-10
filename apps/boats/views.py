from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from .forms import BoatForm, BoatPhotoForm
from .models import Boat


class BoatListView(LoginRequiredMixin, ListView):
    template_name = "boats/list.html"

    def get_queryset(self):
        return Boat.objects.filter(owner=self.request.user).prefetch_related("photos")


class BoatDetailView(DetailView):
    model = Boat
    template_name = "boats/detail.html"
    context_object_name = "boat"


@login_required
def boat_create(request):
    if request.method == "POST":
        form = BoatForm(request.POST)
        if form.is_valid():
            boat = form.save(commit=False)
            boat.owner = request.user
            boat.save()
            return redirect("boats:detail", pk=boat.pk)
    else:
        form = BoatForm()
    return render(request, "boats/form.html", {"form": form, "boat": None})


@login_required
def boat_edit(request, pk):
    boat = get_object_or_404(Boat, pk=pk, owner=request.user)
    if request.method == "POST":
        form = BoatForm(request.POST, instance=boat)
        if form.is_valid():
            form.save()
            return redirect("boats:detail", pk=boat.pk)
    else:
        form = BoatForm(instance=boat)
    return render(request, "boats/form.html", {"form": form, "boat": boat})


@login_required
def boat_add_photo(request, pk):
    boat = get_object_or_404(Boat, pk=pk, owner=request.user)
    if request.method == "POST":
        form = BoatPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.boat = boat
            photo.save()
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "boats/partials/gallery.html",
                    {"boat": boat},
                )
            return redirect("boats:detail", pk=boat.pk)
    else:
        form = BoatPhotoForm()
    return render(request, "boats/partials/photo_form.html", {"form": form, "boat": boat})

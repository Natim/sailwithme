from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from .forms import BoatForm, BoatPhotoForm
from .models import Boat, BoatPhoto


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
            messages.success(request, "Bateau enregistré.")
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
            messages.success(request, "Bateau mis à jour.")
            return redirect("boats:detail", pk=boat.pk)
    else:
        form = BoatForm(instance=boat)
    return render(request, "boats/form.html", {"form": form, "boat": boat})


@login_required
def boat_delete(request, pk):
    boat = get_object_or_404(Boat, pk=pk, owner=request.user)
    if request.method == "POST":
        boat.delete()
        messages.success(request, "Bateau supprimé.")
        return redirect("boats:list")
    return render(request, "boats/confirm_delete.html", {"boat": boat})


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
                    "boats/partials/gallery_item.html",
                    {"boat": boat, "photo": photo},
                )
            messages.success(request, "Photo ajoutée.")
            return redirect("boats:detail", pk=boat.pk)
        if request.headers.get("HX-Request"):
            return render(
                request,
                "boats/partials/photo_form.html",
                {"form": form, "boat": boat},
                status=400,
            )
    else:
        form = BoatPhotoForm()
    return render(request, "boats/partials/photo_form.html", {"form": form, "boat": boat})


@login_required
def boat_photo_delete(request, photo_pk):
    photo = get_object_or_404(BoatPhoto, pk=photo_pk, boat__owner=request.user)
    boat_pk = photo.boat_id
    if photo.image:
        photo.image.delete(save=False)
    photo.delete()
    if request.headers.get("HX-Request"):
        return HttpResponse("")
    messages.success(request, "Photo supprimée.")
    return redirect("boats:detail", pk=boat_pk)

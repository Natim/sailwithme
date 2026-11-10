from pathlib import Path

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.forms_ui import INPUT_CLASS as BOAT_INPUT
from apps.profiles.models import ALLOWED_PROFILE_PHOTO_SUFFIXES

from .models import Boat, BoatPhoto

EQUIPMENT_CHOICES = [
    ("watermaker", _("Watermaker")),
    ("ais", "AIS"),
    ("starlink", _("Starlink / internet")),
    ("autopilot", _("Autopilot")),
    ("dodger", _("Dodger")),
]


class BoatForm(forms.ModelForm):
    equipment = forms.MultipleChoiceField(
        choices=EQUIPMENT_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Boat
        fields = [
            "name",
            "boat_type",
            "model_name",
            "length_ft",
            "year_built",
            "flag",
            "berths",
            "equipment",
            "description",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": BOAT_INPUT}),
            "boat_type": forms.Select(attrs={"class": BOAT_INPUT}),
            "model_name": forms.TextInput(attrs={"class": BOAT_INPUT}),
            "length_ft": forms.NumberInput(attrs={"class": BOAT_INPUT, "step": "0.1"}),
            "year_built": forms.NumberInput(attrs={"class": BOAT_INPUT}),
            "flag": forms.TextInput(attrs={"class": BOAT_INPUT}),
            "berths": forms.NumberInput(attrs={"class": BOAT_INPUT, "min": 1}),
            "description": forms.Textarea(attrs={"rows": 4, "class": BOAT_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            "name": _("Boat name"),
            "boat_type": _("Type"),
            "model_name": _("Model"),
            "length_ft": _("Length (ft)"),
            "year_built": _("Year built"),
            "flag": _("Flag"),
            "berths": _("Berths on board"),
            "equipment": _("Equipment"),
            "description": _("Description"),
        }
        for name, label in labels.items():
            if name in self.fields:
                self.fields[name].label = label
        if self.instance.pk:
            self.fields["equipment"].initial = self.instance.equipment or []

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.equipment = self.cleaned_data.get("equipment", [])
        if commit:
            obj.save()
        return obj


class BoatPhotoForm(forms.ModelForm):
    class Meta:
        model = BoatPhoto
        fields = ["image", "caption", "sort_order"]
        widgets = {
            "image": forms.FileInput(
                attrs={"class": BOAT_INPUT, "accept": "image/jpeg,image/png,image/webp,image/gif"}
            ),
            "caption": forms.TextInput(attrs={"class": BOAT_INPUT}),
            "sort_order": forms.NumberInput(attrs={"class": BOAT_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].label = _("Photo")
        self.fields["caption"].label = _("Caption")
        self.fields["sort_order"].label = _("Display order")

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            return image
        suffix = Path(image.name).suffix.lower()
        if suffix == ".jpeg":
            suffix = ".jpg"
        if suffix not in ALLOWED_PROFILE_PHOTO_SUFFIXES:
            raise forms.ValidationError(_("Accepted formats: JPG, PNG, WebP, or GIF."))
        return image

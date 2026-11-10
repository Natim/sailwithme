from pathlib import Path

from django import forms

from apps.core.forms_ui import INPUT_CLASS as BOAT_INPUT
from apps.profiles.models import ALLOWED_PROFILE_PHOTO_SUFFIXES

from .models import Boat, BoatPhoto

EQUIPMENT_CHOICES = [
    ("watermaker", "Dessalinisateur"),
    ("ais", "AIS"),
    ("starlink", "Starlink / internet"),
    ("autopilot", "Pilote automatique"),
    ("dodger", "Capote de descente"),
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
            "name": "Nom du bateau",
            "boat_type": "Type",
            "model_name": "Modèle",
            "length_ft": "Longueur (pieds)",
            "year_built": "Année de construction",
            "flag": "Pavillon",
            "berths": "Nombre de places à bord (couchettes)",
            "equipment": "Équipement",
            "description": "Description",
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
        self.fields["image"].label = "Photo"
        self.fields["caption"].label = "Légende"
        self.fields["sort_order"].label = "Ordre d'affichage"

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            return image
        suffix = Path(image.name).suffix.lower()
        if suffix == ".jpeg":
            suffix = ".jpg"
        if suffix not in ALLOWED_PROFILE_PHOTO_SUFFIXES:
            raise forms.ValidationError("Format accepté : JPG, PNG, WebP ou GIF.")
        return image

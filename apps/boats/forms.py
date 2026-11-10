from django import forms

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
            "description",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full rounded border p-2"}),
            "boat_type": forms.Select(attrs={"class": "w-full rounded border p-2"}),
            "model_name": forms.TextInput(attrs={"class": "w-full rounded border p-2"}),
            "length_ft": forms.NumberInput(attrs={"class": "w-full rounded border p-2"}),
            "year_built": forms.NumberInput(attrs={"class": "w-full rounded border p-2"}),
            "flag": forms.TextInput(attrs={"class": "w-full rounded border p-2"}),
            "berths": forms.NumberInput(attrs={"class": "w-full rounded border p-2"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "w-full rounded border p-2"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

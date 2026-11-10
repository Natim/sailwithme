from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.forms_ui import INPUT_CLASS
from apps.core.language_choices import LANGUAGE_CHOICES

from .models import Profile

CHECKBOX_CLASS = "rounded border-slate-300 text-teal-600 focus:ring-teal-500"

CERTIFICATION_CHOICES = [
    ("permis_mer", _("Yachtmaster / offshore license")),
    ("stcw", "STCW"),
    ("psc1", _("First aid / PSC1")),
    ("vhf", _("VHF / SRC")),
]

SKILL_CHOICES = [
    ("cooking", _("Cooking")),
    ("mechanics", _("Mechanics")),
    ("electronics", _("Electronics")),
    ("medical", _("First aid")),
    ("celestial", _("Celestial navigation")),
    ("photo", _("Photo / video")),
]


class ProfileBasicsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["pseudo", "role", "bio", "nationality", "home_port", "skill_level", "availability_notes"]
        widgets = {
            "pseudo": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Capitaine_Aurore", "maxlength": "32"}
            ),
            "bio": forms.Textarea(attrs={"rows": 4, "class": INPUT_CLASS, "placeholder": _("A few words about you…")}),
            "role": forms.Select(attrs={"class": INPUT_CLASS}),
            "nationality": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "France"}),
            "home_port": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Lorient"}),
            "skill_level": forms.Select(attrs={"class": INPUT_CLASS}),
            "availability_notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": INPUT_CLASS,
                    "placeholder": _("Availability, cruising windows…"),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pseudo"].label = _("Public nickname")
        self.fields["pseudo"].help_text = _(
            "Shown on listings and reviews. Leave blank for a Marin-xxxxxxxx identifier."
        )
        self.fields["role"].label = _("Role")
        self.fields["bio"].label = _("Bio")
        self.fields["nationality"].label = _("Nationality")
        self.fields["home_port"].label = _("Home port")
        self.fields["skill_level"].label = _("Level")
        self.fields["availability_notes"].label = _("Availability")

    def clean_pseudo(self):
        pseudo = (self.cleaned_data.get("pseudo") or "").strip()
        if not pseudo:
            return ""
        if len(pseudo) < 2:
            raise forms.ValidationError(_("Username must be at least 2 characters."))
        qs = Profile.objects.filter(pseudo__iexact=pseudo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("This username is already taken."))
        return pseudo


class ProfileExperienceForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["nautical_miles", "ocean_crossings", "certifications", "skills"]
        widgets = {
            "nautical_miles": forms.NumberInput(attrs={"class": INPUT_CLASS, "min": 0}),
            "ocean_crossings": forms.NumberInput(attrs={"class": INPUT_CLASS, "min": 0}),
        }

    certifications = forms.MultipleChoiceField(
        label=_("Certifications"),
        choices=CERTIFICATION_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    skills = forms.MultipleChoiceField(
        label=_("Skills"),
        choices=SKILL_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nautical_miles"].label = _("Nautical miles")
        self.fields["ocean_crossings"].label = _("Ocean crossings")
        if self.instance.pk:
            self.fields["certifications"].initial = self.instance.certifications or []
            self.fields["skills"].initial = self.instance.skills or []

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.certifications = self.cleaned_data.get("certifications", [])
        obj.skills = self.cleaned_data.get("skills", [])
        if commit:
            obj.save()
        return obj


class ProfilePreferencesForm(forms.ModelForm):
    languages = forms.MultipleChoiceField(
        label=_("Languages spoken"),
        choices=LANGUAGE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Profile
        fields = [
            "languages",
            "non_smoker",
            "pets_ok",
            "vegetarian_friendly",
            "crew_directory_visible",
            "photo",
        ]
        widgets = {
            "non_smoker": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "pets_ok": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "vegetarian_friendly": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "crew_directory_visible": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "photo": forms.FileInput(attrs={"class": "sr-only"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["non_smoker"].label = _("Non-smoker")
        self.fields["pets_ok"].label = _("Pets welcome")
        self.fields["vegetarian_friendly"].label = _("Vegetarians welcome")
        self.fields["crew_directory_visible"].label = _("Visible in the crew directory")
        if self.instance.pk:
            self.fields["languages"].initial = self.instance.languages or []

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.languages = self.cleaned_data.get("languages", [])
        if commit:
            obj.save()
        return obj

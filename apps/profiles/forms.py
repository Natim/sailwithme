from django import forms

from .models import Profile

CERTIFICATION_CHOICES = [
    ("permis_mer", "Permis mer / Yachtmaster"),
    ("stcw", "STCW"),
    ("psc1", "PSC1 / First aid"),
    ("vhf", "VHF / SRC"),
]

SKILL_CHOICES = [
    ("cooking", "Cuisine"),
    ("mechanics", "Mécanique"),
    ("electronics", "Électronique"),
    ("medical", "Premiers secours"),
    ("celestial", "Navigation astro"),
    ("photo", "Photo / vidéo"),
]

LANGUAGE_CHOICES = [
    ("fr", "Français"),
    ("en", "English"),
    ("es", "Español"),
    ("de", "Deutsch"),
    ("pt", "Português"),
]


class ProfileBasicsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["role", "bio", "nationality", "home_port", "skill_level", "availability_notes"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "class": "w-full rounded border p-2"}),
            "role": forms.Select(attrs={"class": "w-full rounded border p-2"}),
            "nationality": forms.TextInput(attrs={"class": "w-full rounded border p-2"}),
            "home_port": forms.TextInput(attrs={"class": "w-full rounded border p-2"}),
            "skill_level": forms.Select(attrs={"class": "w-full rounded border p-2"}),
            "availability_notes": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded border p-2"}),
        }


class ProfileExperienceForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["nautical_miles", "ocean_crossings", "certifications", "skills"]
        widgets = {
            "nautical_miles": forms.NumberInput(attrs={"class": "w-full rounded border p-2"}),
            "ocean_crossings": forms.NumberInput(attrs={"class": "w-full rounded border p-2"}),
        }

    certifications = forms.MultipleChoiceField(
        choices=CERTIFICATION_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    skills = forms.MultipleChoiceField(
        choices=SKILL_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        widgets = {"photo": forms.ClearableFileInput(attrs={"class": "w-full"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["languages"].initial = self.instance.languages or []

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.languages = self.cleaned_data.get("languages", [])
        if commit:
            obj.save()
        return obj

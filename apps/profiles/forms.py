from django import forms

from apps.core.forms_ui import INPUT_CLASS

from .models import Profile

CHECKBOX_CLASS = "rounded border-slate-300 text-teal-600 focus:ring-teal-500"

CERTIFICATION_CHOICES = [
    ("permis_mer", "Permis mer / Yachtmaster"),
    ("stcw", "STCW"),
    ("psc1", "PSC1 / premiers secours"),
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
            "bio": forms.Textarea(attrs={"rows": 4, "class": INPUT_CLASS, "placeholder": "Quelques mots sur toi…"}),
            "role": forms.Select(attrs={"class": INPUT_CLASS}),
            "nationality": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "France"}),
            "home_port": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Lorient"}),
            "skill_level": forms.Select(attrs={"class": INPUT_CLASS}),
            "availability_notes": forms.Textarea(
                attrs={"rows": 3, "class": INPUT_CLASS, "placeholder": "Disponibilités, fenêtres de croisière…"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].label = "Rôle"
        self.fields["bio"].label = "Présentation"
        self.fields["nationality"].label = "Nationalité"
        self.fields["home_port"].label = "Port d'attache"
        self.fields["skill_level"].label = "Niveau"
        self.fields["availability_notes"].label = "Disponibilités"


class ProfileExperienceForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["nautical_miles", "ocean_crossings", "certifications", "skills"]
        widgets = {
            "nautical_miles": forms.NumberInput(attrs={"class": INPUT_CLASS, "min": 0}),
            "ocean_crossings": forms.NumberInput(attrs={"class": INPUT_CLASS, "min": 0}),
        }

    certifications = forms.MultipleChoiceField(
        label="Certifications",
        choices=CERTIFICATION_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    skills = forms.MultipleChoiceField(
        label="Compétences",
        choices=SKILL_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nautical_miles"].label = "Milles nautiques"
        self.fields["ocean_crossings"].label = "Traversées océaniques"
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
        label="Langues parlées",
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
        self.fields["non_smoker"].label = "Non-fumeur"
        self.fields["pets_ok"].label = "Animaux acceptés"
        self.fields["vegetarian_friendly"].label = "Végétarien bienvenu"
        self.fields["crew_directory_visible"].label = "Visible dans l'annuaire équipiers"
        if self.instance.pk:
            self.fields["languages"].initial = self.instance.languages or []

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.languages = self.cleaned_data.get("languages", [])
        if commit:
            obj.save()
        return obj

from django import forms
from django.contrib.gis.geos import Point

from apps.profiles.models import SkillLevel

from .iso_weeks import SEASON_SHORTCUTS
from .models import Listing, ListingApplication, ListingKind, SearchAlert

LISTING_INPUT = "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"


class ListingForm(forms.ModelForm):
    departure_lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    departure_lng = forms.FloatField(required=False, widget=forms.HiddenInput())
    arrival_lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    arrival_lng = forms.FloatField(required=False, widget=forms.HiddenInput())
    season_shortcut = forms.ChoiceField(
        label="Raccourci saison",
        required=False,
        choices=[("", "—")] + [(k, v["label"]) for k, v in SEASON_SHORTCUTS.items()],
        widget=forms.Select(attrs={"class": LISTING_INPUT}),
    )

    class Meta:
        model = Listing
        fields = [
            "kind",
            "title",
            "description",
            "programme_type",
            "boat",
            "departure_name",
            "arrival_name",
            "year",
            "week_from",
            "week_to",
            "duration_days",
            "berths_available",
            "daily_contribution_eur",
            "min_skill_level",
            "languages_on_board",
            "requirements",
            "flexibility_nm",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5, "class": LISTING_INPUT}),
            "title": forms.TextInput(attrs={"class": LISTING_INPUT}),
            "kind": forms.Select(attrs={"class": LISTING_INPUT}),
            "programme_type": forms.Select(attrs={"class": LISTING_INPUT}),
            "boat": forms.Select(attrs={"class": LISTING_INPUT}),
            "departure_name": forms.TextInput(attrs={"class": LISTING_INPUT}),
            "arrival_name": forms.TextInput(attrs={"class": LISTING_INPUT}),
            "year": forms.NumberInput(attrs={"class": LISTING_INPUT}),
            "week_from": forms.NumberInput(attrs={"class": LISTING_INPUT}),
            "week_to": forms.NumberInput(attrs={"class": LISTING_INPUT}),
            "duration_days": forms.NumberInput(attrs={"class": LISTING_INPUT}),
            "berths_available": forms.NumberInput(attrs={"class": LISTING_INPUT}),
            "daily_contribution_eur": forms.NumberInput(attrs={"class": LISTING_INPUT, "step": "0.01"}),
            "requirements": forms.Textarea(attrs={"rows": 3, "class": LISTING_INPUT}),
            "flexibility_nm": forms.NumberInput(attrs={"class": LISTING_INPUT}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["boat"].queryset = user.boats.all()
        self.fields["boat"].required = False
        self.fields["boat"].empty_label = "— Aucun —"
        labels = {
            "kind": "Type d'annonce",
            "title": "Titre",
            "description": "Description",
            "programme_type": "Programme",
            "boat": "Bateau",
            "departure_name": "Nom du départ",
            "arrival_name": "Nom de l'arrivée",
            "year": "Année",
            "week_from": "Semaine de début (ISO)",
            "week_to": "Semaine de fin (ISO)",
            "duration_days": "Durée (jours)",
            "berths_available": "Couchettes disponibles",
            "daily_contribution_eur": "Participation journalière (€)",
            "min_skill_level": "Niveau minimum",
            "languages_on_board": "Langues à bord",
            "requirements": "Prérequis",
            "flexibility_nm": "Souplesse sur la route (mn)",
        }
        for name, label in labels.items():
            if name in self.fields:
                self.fields[name].label = label
        self.fields["min_skill_level"].required = False
        self.fields["min_skill_level"].widget = forms.Select(
            attrs={"class": LISTING_INPUT},
            choices=[("", "—")] + list(SkillLevel.choices),
        )
        self.fields["languages_on_board"].required = False
        if "languages_on_board" in self.fields:
            self.fields["languages_on_board"].help_text = "Codes langue séparés par des virgules (ex. fr, en)."

    def clean(self):
        cleaned = super().clean()
        shortcut = cleaned.get("season_shortcut")
        year = cleaned.get("year")
        if shortcut and year:
            spec = SEASON_SHORTCUTS[shortcut]
            cleaned["week_from"] = spec["week_from"]
            cleaned["week_to"] = spec["week_to"]
        lat = cleaned.get("departure_lat")
        lng = cleaned.get("departure_lng")
        alat = cleaned.get("arrival_lat")
        alng = cleaned.get("arrival_lng")
        if lat is not None and lng is not None:
            cleaned["departure_point"] = Point(lng, lat, srid=4326)
        elif self.instance.pk and self.instance.departure_point:
            cleaned["departure_point"] = self.instance.departure_point
        if alat is not None and alng is not None:
            cleaned["arrival_point"] = Point(alng, alat, srid=4326)
        elif self.instance.pk and self.instance.arrival_point:
            cleaned["arrival_point"] = self.instance.arrival_point
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.author = self.user
        obj.departure_point = self.cleaned_data.get("departure_point")
        obj.arrival_point = self.cleaned_data.get("arrival_point")
        if commit:
            obj.save()
        return obj


class ListingSearchForm(forms.Form):
    q = forms.CharField(
        label="Mots-clés",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "w-full rounded-lg border border-slate-300 px-3 py-2", "placeholder": "Route, escale…"}
        ),
    )
    kind = forms.ChoiceField(
        label="Type",
        required=False,
        choices=[("", "Tous")] + list(ListingKind.choices),
        widget=forms.Select(attrs={"class": "w-full rounded-lg border border-slate-300 px-3 py-2"}),
    )
    programme_type = forms.ChoiceField(
        label="Programme",
        required=False,
        choices=[("", "Tous")],
        widget=forms.Select(attrs={"class": "w-full rounded-lg border border-slate-300 px-3 py-2"}),
    )
    departure_port = forms.ModelChoiceField(
        label="Départ (escale)",
        queryset=None,
        required=False,
        empty_label="— Tous —",
        widget=forms.Select(attrs={"class": "w-full rounded-lg border border-slate-300 px-3 py-2"}),
    )
    arrival_port = forms.ModelChoiceField(
        label="Arrivée (escale)",
        queryset=None,
        required=False,
        empty_label="— Tous —",
        widget=forms.Select(attrs={"class": "w-full rounded-lg border border-slate-300 px-3 py-2"}),
    )
    departure_lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    departure_lng = forms.FloatField(required=False, widget=forms.HiddenInput())
    departure_radius_nm = forms.IntegerField(
        label="Rayon départ (mn)",
        required=False,
        initial=150,
        min_value=10,
        max_value=2000,
        widget=forms.NumberInput(attrs={"class": "w-full rounded-lg border border-slate-300 px-3 py-2"}),
    )
    arrival_lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    arrival_lng = forms.FloatField(required=False, widget=forms.HiddenInput())
    arrival_radius_nm = forms.IntegerField(
        label="Rayon arrivée (mn)",
        required=False,
        initial=150,
        min_value=10,
        max_value=2000,
        widget=forms.NumberInput(attrs={"class": "w-full rounded-lg border border-slate-300 px-3 py-2"}),
    )
    year = forms.IntegerField(
        label="Année",
        required=False,
        min_value=2024,
        max_value=2035,
        widget=forms.NumberInput(attrs={"class": "w-full rounded-lg border border-slate-300 px-3 py-2"}),
    )
    week_from = forms.IntegerField(
        label="Semaine de",
        required=False,
        min_value=1,
        max_value=53,
        widget=forms.NumberInput(attrs={"class": "w-full rounded-lg border border-slate-300 px-3 py-2"}),
    )
    week_to = forms.IntegerField(
        label="Semaine à",
        required=False,
        min_value=1,
        max_value=53,
        widget=forms.NumberInput(attrs={"class": "w-full rounded-lg border border-slate-300 px-3 py-2"}),
    )
    sort = forms.ChoiceField(
        label="Tri",
        required=False,
        initial="relevance",
        choices=[
            ("relevance", "Pertinence"),
            ("date", "Date de départ"),
        ],
        widget=forms.Select(attrs={"class": "w-full rounded-lg border border-slate-300 px-3 py-2"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Port, ProgrammeType

        self.fields["departure_port"].queryset = Port.objects.all()
        self.fields["arrival_port"].queryset = Port.objects.all()
        self.fields["programme_type"].choices = [("", "Tous")] + list(ProgrammeType.choices)

    def clean(self):
        cleaned = super().clean()
        dep_port = cleaned.get("departure_port")
        arr_port = cleaned.get("arrival_port")
        if dep_port and dep_port.location:
            cleaned["departure_lat"] = dep_port.location.y
            cleaned["departure_lng"] = dep_port.location.x
        if arr_port and arr_port.location:
            cleaned["arrival_lat"] = arr_port.location.y
            cleaned["arrival_lng"] = arr_port.location.x
        year = cleaned.get("year")
        wf = cleaned.get("week_from")
        wt = cleaned.get("week_to")
        if any(x is not None for x in (year, wf, wt)) and not all(x is not None for x in (year, wf, wt)):
            raise forms.ValidationError(
                "Pour filtrer par dates, renseignez l'année et les deux semaines (de / à)."
            )
        return cleaned


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = ListingApplication
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": LISTING_INPUT,
                    "placeholder": "Présentez-vous en quelques lignes…",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"].label = "Message au skipper"


class SearchAlertForm(forms.ModelForm):
    class Meta:
        model = SearchAlert
        fields = [
            "name",
            "departure_lat",
            "departure_lng",
            "departure_radius_nm",
            "arrival_lat",
            "arrival_lng",
            "arrival_radius_nm",
            "year",
            "week_from",
            "week_to",
            "programme_type",
            "kind",
        ]
        widgets = {
            k: forms.HiddenInput()
            for k in (
                "departure_lat",
                "departure_lng",
                "arrival_lat",
                "arrival_lng",
                "year",
                "week_from",
                "week_to",
                "programme_type",
                "kind",
            )
        }

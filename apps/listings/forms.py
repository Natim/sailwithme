from django import forms
from django.contrib.gis.geos import Point

from .iso_weeks import SEASON_SHORTCUTS
from .models import Listing, ListingApplication, ListingKind, SearchAlert


class ListingForm(forms.ModelForm):
    departure_lat = forms.FloatField(required=False)
    departure_lng = forms.FloatField(required=False)
    arrival_lat = forms.FloatField(required=False)
    arrival_lng = forms.FloatField(required=False)
    season_shortcut = forms.ChoiceField(
        required=False,
        choices=[("", "—")] + [(k, v["label"]) for k, v in SEASON_SHORTCUTS.items()],
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
            "description": forms.Textarea(attrs={"rows": 5, "class": "w-full rounded border p-2"}),
            "title": forms.TextInput(attrs={"class": "w-full rounded border p-2"}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["boat"].queryset = user.boats.all()
        self.fields["boat"].required = False

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
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "rounded border p-2"}))
    kind = forms.ChoiceField(
        required=False,
        choices=[("", "Tous")] + list(ListingKind.choices),
    )
    programme_type = forms.ChoiceField(required=False, choices=[("", "Tous")])
    departure_lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    departure_lng = forms.FloatField(required=False, widget=forms.HiddenInput())
    departure_radius_nm = forms.IntegerField(
        required=False,
        initial=150,
        widget=forms.NumberInput(attrs={"class": "w-24 rounded border p-2"}),
    )
    arrival_lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    arrival_lng = forms.FloatField(required=False, widget=forms.HiddenInput())
    arrival_radius_nm = forms.IntegerField(
        required=False,
        initial=150,
        widget=forms.NumberInput(attrs={"class": "w-24 rounded border p-2"}),
    )
    year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"class": "w-24 rounded border p-2"}))
    week_from = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=53,
        widget=forms.NumberInput(attrs={"class": "w-20 rounded border p-2"}),
    )
    week_to = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=53,
        widget=forms.NumberInput(attrs={"class": "w-20 rounded border p-2"}),
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ("relevance", "Pertinence"),
            ("date", "Date de départ"),
        ],
        widget=forms.Select(attrs={"class": "rounded border p-2"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import ProgrammeType

        self.fields["programme_type"].choices = [("", "Tous")] + list(ProgrammeType.choices)


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = ListingApplication
        fields = ["message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4, "class": "w-full rounded border p-2"})}


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

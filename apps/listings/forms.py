from django import forms
from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _

from apps.core.language_choices import LANGUAGE_CHOICES
from apps.profiles.models import SkillLevel

from .iso_weeks import SEASON_SHORTCUTS
from .models import Listing, ListingApplication, ListingKind, SearchAlert

from apps.core.forms_ui import INPUT_CLASS as LISTING_INPUT


class ListingForm(forms.ModelForm):
    departure_lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    departure_lng = forms.FloatField(required=False, widget=forms.HiddenInput())
    arrival_lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    arrival_lng = forms.FloatField(required=False, widget=forms.HiddenInput())
    season_shortcut = forms.ChoiceField(
        label=_("Season shortcut"),
        required=False,
        choices=[("", "—")] + [(k, v["label"]) for k, v in SEASON_SHORTCUTS.items()],
        widget=forms.Select(attrs={"class": LISTING_INPUT}),
    )
    languages_on_board = forms.MultipleChoiceField(
        label=_("Languages on board"),
        choices=LANGUAGE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
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
        self.fields["boat"].empty_label = _("— None —")
        labels = {
            "kind": _("Listing type"),
            "title": _("Title"),
            "description": _("Description"),
            "programme_type": _("Programme"),
            "boat": _("Boat"),
            "departure_name": _("Departure name"),
            "arrival_name": _("Arrival name"),
            "year": _("Year"),
            "week_from": _("Start week (ISO)"),
            "week_to": _("End week (ISO)"),
            "duration_days": _("Duration (days)"),
            "berths_available": _("Berths available"),
            "daily_contribution_eur": _("Daily contribution (€)"),
            "min_skill_level": _("Minimum level"),
            "languages_on_board": _("Languages on board"),
            "requirements": _("Requirements"),
            "flexibility_nm": _("Route flexibility (nm)"),
        }
        for name, label in labels.items():
            if name in self.fields:
                self.fields[name].label = label
        self.fields["min_skill_level"].required = False
        self.fields["min_skill_level"].widget = forms.Select(
            attrs={"class": LISTING_INPUT},
            choices=[("", "—")] + list(SkillLevel.choices),
        )
        if self.instance.pk:
            self.fields["languages_on_board"].initial = self.instance.languages_on_board or []
            if self.instance.departure_point:
                self.fields["departure_lat"].initial = float(self.instance.departure_point.y)
                self.fields["departure_lng"].initial = float(self.instance.departure_point.x)
            if self.instance.arrival_point:
                self.fields["arrival_lat"].initial = float(self.instance.arrival_point.y)
                self.fields["arrival_lng"].initial = float(self.instance.arrival_point.x)

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
        if not cleaned.get("departure_point") or not cleaned.get("arrival_point"):
            raise forms.ValidationError(
                _("Click the map to set departure then arrival before publishing.")
            )
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.author = self.user
        obj.departure_point = self.cleaned_data.get("departure_point")
        obj.arrival_point = self.cleaned_data.get("arrival_point")
        obj.languages_on_board = self.cleaned_data.get("languages_on_board", [])
        if commit:
            obj.save()
        return obj


class ListingSearchForm(forms.Form):
    q = forms.CharField(
        label=_("Keywords"),
        required=False,
        widget=forms.TextInput(
            attrs={"class": LISTING_INPUT, "placeholder": _("Route, port…")}
        ),
    )
    kind = forms.ChoiceField(
        label=_("Type"),
        required=False,
        choices=[("", _("All"))] + list(ListingKind.choices),
        widget=forms.Select(attrs={"class": LISTING_INPUT}),
    )
    programme_type = forms.ChoiceField(
        label=_("Programme"),
        required=False,
        choices=[("", _("All"))],
        widget=forms.Select(attrs={"class": LISTING_INPUT}),
    )
    departure_port = forms.ModelChoiceField(
        label=_("Departure (port)"),
        queryset=None,
        required=False,
        empty_label=_("— Any —"),
        widget=forms.Select(attrs={"class": LISTING_INPUT}),
    )
    arrival_port = forms.ModelChoiceField(
        label=_("Arrival (port)"),
        queryset=None,
        required=False,
        empty_label=_("— Any —"),
        widget=forms.Select(attrs={"class": LISTING_INPUT}),
    )
    departure_lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    departure_lng = forms.FloatField(required=False, widget=forms.HiddenInput())
    departure_radius_nm = forms.IntegerField(
        label=_("Departure radius (nm)"),
        required=False,
        initial=150,
        min_value=10,
        max_value=2000,
        widget=forms.NumberInput(attrs={"class": LISTING_INPUT}),
    )
    arrival_lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    arrival_lng = forms.FloatField(required=False, widget=forms.HiddenInput())
    arrival_radius_nm = forms.IntegerField(
        label=_("Arrival radius (nm)"),
        required=False,
        initial=150,
        min_value=10,
        max_value=2000,
        widget=forms.NumberInput(attrs={"class": LISTING_INPUT}),
    )
    year = forms.IntegerField(
        label=_("Year"),
        required=False,
        min_value=2024,
        max_value=2035,
        widget=forms.NumberInput(attrs={"class": LISTING_INPUT}),
    )
    week_from = forms.IntegerField(
        label=_("Week from"),
        required=False,
        min_value=1,
        max_value=53,
        widget=forms.NumberInput(attrs={"class": LISTING_INPUT}),
    )
    week_to = forms.IntegerField(
        label=_("Week to"),
        required=False,
        min_value=1,
        max_value=53,
        widget=forms.NumberInput(attrs={"class": LISTING_INPUT}),
    )
    sort = forms.ChoiceField(
        label=_("Sort"),
        required=False,
        initial="relevance",
        choices=[
            ("relevance", _("Relevance")),
            ("date", _("Departure date")),
        ],
        widget=forms.Select(attrs={"class": LISTING_INPUT}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Port, ProgrammeType

        self.fields["departure_port"].queryset = Port.objects.all()
        self.fields["arrival_port"].queryset = Port.objects.all()
        self.fields["programme_type"].choices = [("", _("All"))] + list(ProgrammeType.choices)

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
                _("To filter by date, enter the year and both weeks (from / to).")
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
                    "placeholder": _("Introduce yourself in a few lines…"),
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"].label = _("Message to the skipper")


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

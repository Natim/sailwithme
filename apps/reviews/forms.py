from django import forms

from .models import Review

from apps.core.forms_ui import INPUT_CLASS as REVIEW_INPUT

REVIEW_RATING = "input w-20 max-w-full"


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            "rating_overall",
            "rating_seamanship",
            "rating_reliability",
            "rating_atmosphere",
            "rating_safety",
            "rating_commitment",
            "comment",
        ]
        widgets = {
            "rating_overall": forms.NumberInput(attrs={"min": 1, "max": 5, "class": REVIEW_RATING}),
            "rating_seamanship": forms.NumberInput(attrs={"min": 1, "max": 5, "class": REVIEW_RATING}),
            "rating_reliability": forms.NumberInput(attrs={"min": 1, "max": 5, "class": REVIEW_RATING}),
            "rating_atmosphere": forms.NumberInput(attrs={"min": 1, "max": 5, "class": REVIEW_RATING}),
            "rating_safety": forms.NumberInput(attrs={"min": 1, "max": 5, "class": REVIEW_RATING}),
            "rating_commitment": forms.NumberInput(attrs={"min": 1, "max": 5, "class": REVIEW_RATING}),
            "comment": forms.Textarea(attrs={"rows": 4, "class": REVIEW_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            "rating_overall": "Note globale (1–5)",
            "rating_seamanship": "Savoir-faire marin",
            "rating_reliability": "Fiabilité",
            "rating_atmosphere": "Ambiance",
            "rating_safety": "Sécurité",
            "rating_commitment": "Engagement",
            "comment": "Commentaire",
        }
        for name, label in labels.items():
            self.fields[name].label = label

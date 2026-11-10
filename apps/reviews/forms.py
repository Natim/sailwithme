from django import forms

from .models import Review


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
            "rating_overall": forms.NumberInput(attrs={"min": 1, "max": 5, "class": "w-20 border rounded p-1"}),
            "comment": forms.Textarea(attrs={"rows": 4, "class": "w-full border rounded p-2"}),
        }

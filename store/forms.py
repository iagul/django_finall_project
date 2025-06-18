from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        label="Rating",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Rating (1-5)",
        }),
        error_messages={
            "min_value": "Rating must be at least 1.",
            "max_value": "Rating cannot be more than 5.",
        },
    )
    comment = forms.CharField(
        required=False,
        label="Comment",
        widget=forms.Textarea(attrs={
            "rows": 3,
            "class": "form-control",
            "placeholder": "Write your comment here...",
        }),
    )

    class Meta:
        model = Review
        fields = ["rating", "comment"]

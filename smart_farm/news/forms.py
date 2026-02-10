from django import forms
from .models import News

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ["title", "slug", "content", "image", "is_published"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Başlıq..."
            }),
            "slug": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "slug-link"
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Xəbər mətni..."
            }),
            "is_published": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

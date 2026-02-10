from django import forms
from .models import Application


class VacancyApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['name', 'email', 'phone', 'cover_letter', 'cv']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows':4, 'placeholder':'Qısa motivasiya məktubu...'}),
            'name': forms.TextInput(attrs={'placeholder':'Ad, Soyad'}),
            'email': forms.EmailInput(attrs={'placeholder':'example@mail.com'}),
            'phone': forms.TextInput(attrs={'placeholder':'+994 ...'}),
        }
        labels = {
            'name': 'Ad, Soyad',
            'email': 'Email Ünvanı',
            'phone': 'Telefon Nömrəsi',
            'cover_letter': 'Motivasiya Məktubu',
            'cv': 'CV Yüklə',
        }
        help_texts = {
            'cv': 'Zəhmət olmasa CV-nizi PDF formatında yükləyin.',
        }

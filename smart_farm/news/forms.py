from django import forms
from .models import News


class NewsForm(forms.ModelForm):
    slug = forms.CharField(
        label='URL (slug)',
        help_text='Boş buraxsanız başlıqdan avtomatik yaranır.',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'torpaq-nemligi',
        })
    )
    class Meta:
        model = News
        fields = ['title', 'slug', 'image', 'content', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Xəbərin başlığını daxil edin...',
            }),
             
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Xəbərin məzmunu...',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'title':        'Başlıq',
            'slug':         'URL (slug)',
            'image':        'Örtük şəkli',
            'content':      'Məzmun',
            'is_published': 'Dərc edilib',
        }
        help_texts = {
            'slug': 'Yalnız kiçik hərflər, rəqəmlər və tire. Məs: yeni-texnologiya-2026',
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', '')
        replacements = {
            'ə':'e','ö':'o','ü':'u','ı':'i','ğ':'g',
            'ş':'s','ç':'c','Ə':'e','Ö':'o','Ü':'u',
            'İ':'i','Ğ':'g','Ş':'s','Ç':'c'
        }
        for az, lat in replacements.items():
            slug = slug.replace(az, lat)
        slug = slug.lower().replace(' ', '-')
        return slug

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'size'):
            if image.size > 8 * 1024 * 1024:
                raise forms.ValidationError('Şəkil ölçüsü 8MB-dan çox ola bilməz.')
        return image
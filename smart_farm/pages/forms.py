from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name','email','subject','message']
        widgets = {
    'name':    forms.TextInput(attrs={'placeholder':'Ad, Soyad'}),
    'email':   forms.EmailInput(attrs={'placeholder':'example@mail.com'}),
    'subject': forms.TextInput(attrs={'placeholder':'Mövzu'}),
    'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Mesajınızı yazın...'}),
}

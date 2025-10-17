from django import forms 
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    farm_name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20,required=False)
    location = forms.CharField(max_length=255,required=False)


    class Meta:
        model =CustomUser
        fields = ('username','email','farm_name','phone','location','password1','password2')
    
        def save(self, commit=True):
            user = super().save(commit=False)
            user.email = self.cleaned_data.get('email')
            user.farm_name = self.cleaned_data.get('farm_name')
            user.phone = self.cleaned_data.get('phone')
            user.location = self.cleaned_data.get('location')

            if commit:
                user.save()

            return user
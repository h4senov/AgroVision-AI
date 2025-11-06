from django import forms 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True,label='Email')
    farm_name = forms.CharField(max_length=100, required=False,label='Fermer adı')
    phone = forms.CharField(max_length=20,required=False,label='Telefon')
    location = forms.CharField(max_length=255,required=False,label='Yerləşdiyi yer')
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES, 
        initial='farmer',
        label='Rol'
    )
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'farm_name', 'phone', 
                  'location', 'role', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.farm_name = self.cleaned_data.get('farm_name')
        user.phone = self.cleaned_data.get('phone')
        user.location = self.cleaned_data.get('location')
        user.role = self.cleaned_data.get('role')

        if commit:
            user.save()
        return user  
    
class CustomUserUpdateForm(UserChangeForm):
    password = None 
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'farm_name', 'phone', 'location', 'role')
        labels = {
            'username': 'İstifadəçi adı',
            'email': 'Email',
            'farm_name': 'Ferma adı', 
            'phone': 'Telefon',
            'location': 'Yerləşdiyi yer',
            'role': 'Rol'
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Köhnə şifrə'}),
        label='Köhnə şifrə'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Yeni şifrə'}),
        label='Yeni şifrə'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Yeni şifrə təsdiqi'}),
        label='Yeni şifrə təsdiqi'
    )

class UserDeactivationForm(forms.Form):
    deactivate_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Deaktivasiya səbəbini qeyd edin...'
        }),
        label='Deaktivasiya səbəbi',
        required=True
    )
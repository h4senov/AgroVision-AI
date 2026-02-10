from django import forms 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser

# users/forms.py

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    farm_name = forms.CharField(max_length=100, required=False, label='Fermer adı')
    phone = forms.CharField(max_length=20, required=False, label='Telefon')
    location = forms.CharField(max_length=255, required=False, label='Yerləşdiyi yer')
    
    # DİQQƏT: role sahəsini buradan sildim. İstifadəçi qeydiyyatda rol seçməməlidir.
    # Model-də onsuz da default='guest' var.
    terms_confirmed = forms.BooleanField(
        required=True,
        label="İstifadə qaydaları ilə razıyam",
        error_messages={'required': 'Qeydiyyatı tamamlamaq üçün qaydalarla razılaşmalısınız.'}
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # terms_confirmed bura düşmür, çünki modeldə yoxdur, sadəcə formadadır.
        fields = UserCreationForm.Meta.fields + ('email', 'farm_name', 'phone', 'location') # role sildik

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            # Checkbox üçün ayrıca stil lazımdır, ona form-control vermirik
            if field != 'terms_confirmed':
                self.fields[field].widget.attrs.update({'class': 'form-control shadow-none'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-check-input shadow-none'})

    # Əgər mütləq hamı 'farmer' olsun istəyirsənsə, save metodunu belə yaza bilərsən:
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'farmer'  # Hamı avtomatik fermer olur
        if commit:
            user.save()
        return user
    
class CustomUserUpdateForm(UserChangeForm):
    password = None  # Şifrə dəyişməyəcək, bunun üçün ayrı formun var zaten

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'farm_name', 'phone', 'location', 'role', 'avatar') # avatar əlavə edildi
        labels = {
            'username': 'İstifadəçi adı',
            'email': 'Email',
            'farm_name': 'Ferma adı', 
            'phone': 'Telefon',
            'location': 'Yerləşdiyi yer',
            'role': 'Rol',
            'avatar': 'Profil şəkli'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bütün sahələrə dinamik olaraq Bootstrap klassı əlavə edirik
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control shadow-none'})
        
        # Əgər istifadəçi admin deyilsə, rolunu özü dəyişə bilməsin
        instance = kwargs.get('instance')
        if instance and not instance.can_manage_system():
            self.fields['role'].disabled = True # və ya self.fields.pop('role')

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
from django import forms
from .models import Sensor, SensorData

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = [
            'field', 'name', 'sensor_code', 'sensor_type', 'description',
            'installation_date', 'latitude', 'longitude', 'battery_level',
            'data_interval', 'is_active'
        ]
        widgets = {
            'field': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sensor adını daxil edin...'}),
            'sensor_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SEN-001'}),
            'sensor_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Sensor haqqında əlavə məlumat...'}),
            'installation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'placeholder': '40.4093'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'placeholder': '49.8671'}),
            'battery_level': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0', 'max': '100'}),
            'data_interval': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '1'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'field': 'Sahə',
            'name': 'Sensor adı',
            'sensor_code': 'Sensor kodu',
            'sensor_type': 'Sensor növü',
            'description': 'Təsvir',
            'installation_date': 'Qurulma tarixi',
            'latitude': 'Enlik',
            'longitude': 'Uzunluq',
            'battery_level': 'Batareya səviyyəsi (%)',
            'data_interval': 'Məlumat intervalı (dəq)',
            'is_active': 'Aktiv',
        }

class SensorSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Axtarış',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sensor adına görə axtar...'
        })
    )

class SensorFilterForm(forms.Form):
    sensor_type = forms.ChoiceField(
        choices=[('', 'Bütün sensor növləri')] + Sensor.SENSOR_TYPES,
        required=False,
        label='Sensor növü',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Bütün statuslar'), ('active', 'Aktiv'), ('inactive', 'Qeyri-aktiv')],
        required=False,
        label='Status',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    battery_level = forms.ChoiceField(
        choices=[('', 'Bütün batareyalar'), ('high', 'Yüksək (>70%)'), ('medium', 'Orta (30-70%)'), ('low', 'Aşağı (<30%)')],
        required=False,
        label='Batareya səviyyəsi',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
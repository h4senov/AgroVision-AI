from django import forms
from .models import WeatherData


class WeatherDataForm(forms.ModelForm):
    class Meta:
        model = WeatherData
        fields = [
            'field', 'weather_date',
            'temperature_max', 'temperature_min', 'temperature_avg',
            'humidity_avg', 'precipitation_mm',
            'wind_speed_avg', 'wind_speed_max',
            'weather_condition',
        ]
        labels = {
            'field': 'Sahə',
            'weather_date': 'Hava tarixi',
            'temperature_max': 'Maksimum temperatur (°C)',
            'temperature_min': 'Minimum temperatur (°C)',
            'temperature_avg': 'Orta temperatur (°C)',
            'humidity_avg': 'Orta rütubət (%)',
            'precipitation_mm': 'Yağıntı (mm)',
            'wind_speed_avg': 'Orta külək sürəti (m/s)',
            'wind_speed_max': 'Maksimum külək sürəti (m/s)',
            'weather_condition': 'Hava şəraiti',
        }
        widgets = {
            'weather_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'temperature_max': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'temperature_min': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'temperature_avg': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'humidity_avg': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'precipitation_mm': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'wind_speed_avg': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'wind_speed_max': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'weather_condition': forms.Select(attrs={'class': 'form-control'}),
            'field': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):

        from fields.models import Field    


        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["field"].queryset = Field.objects.filter(user=user)

    def clean(self):
        cleaned = super().clean()
        tmin = cleaned.get('temperature_min')
        tmax = cleaned.get('temperature_max')
        if tmin is not None and tmax is not None and tmin > tmax:
            self.add_error('temperature_min', 'Minimum temperatur maksimumdan böyük ola bilməz.')
        return cleaned
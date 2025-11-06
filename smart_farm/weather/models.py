from django.db import models # verilernler bazasi ile islemeye imkan verir
from django.conf import settings # smartfarmin settingsine daxil olmaq ucundur 
from fields.models import Field # field adli obyekti getirir

class WeatherData(models.Model):
    WEATHER_CONDITIONS = [
        ('sunny', '☀️ Günəşli'),
        ('cloudy', '☁️ Buludlu'),
        ('rainy', '🌧️ Yağmurlu'),
        ('stormy', '⛈️ Tufanlı'),
        ('foggy', '🌫️ Dumanlı'),
        ('snowy', '❄️ Qarlı'),
    ]
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='weather_data')
    weather_date = models.DateField(verbose_name='Hava tarixi')

    temperature_max = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Maksimum temperatur (°C)')
    temperature_min = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Minimum temperatur (°C)')
    temperature_avg = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Orta temperatur (°C)')

    humidity_avg = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Orta rütubət (%)')
    humidity_max = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Maksimum rütubət (%)')
    humidity_min = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Minimum rütubət (%)')

    precipitation_mm = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Yağıntı (mm)')
    wind_speed_avg = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Orta külək sürəti (m/s)')
    wind_speed_max = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Maksimum külək sürəti (m/s)')
    wind_direction_degrees = models.IntegerField(null=True, blank=True, verbose_name='Külək istiqaməti (dərəcə)')
    solar_radiation_mj_m2 = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Günəş radiasiyası (MJ/m²)')
    evapotranspiration_mm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Evapotranspirasiya (mm)')

    weather_condition = models.CharField(max_length=20, choices=WEATHER_CONDITIONS, verbose_name='Hava şəraiti')
    data_source = models.CharField(max_length=50, default='api', verbose_name='Məlumat mənbəyi')
    forecast_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Proqnoz dəqiqliyi (%)')

    created_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'Hava məlumatı'
        verbose_name_plural = 'Hava məlumatları'
        unique_together = ['field', 'weather_date']
        ordering = ['-weather_date']

    def __str__(self):
        
        return f"{self.field.name} - {self.weather_date} - {self.get_weather_condition_display()}"
    

    def is_rainy_day(self):
         
        return self.precipitation_mm > 0
    

    def get_temperature_range(self):

        return f"{self.temperature_min}°C - {self.temperature_max}°C"
    

    def get_weather_risk_level(self):
        
        if self.precipitation_mm > 50 or self.wind_speed_max > 20:
            return 'high'
        elif self.precipitation_mm > 20 or self.wind_speed_max > 15:
            return 'medium'
        else:
            return 'low'
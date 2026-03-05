from django.db import models
from fields.models import Field


class WeatherManager(models.Manager):
    def get_rainy_fields(self, user, days=7):
        from django.utils import timezone
        from datetime import timedelta
        start_date = timezone.now().date() - timedelta(days=days)
        return Field.objects.filter(
            user=user,
            weather_data__precipitation_mm__gt=0,
            weather_data__weather_date__gte=start_date
        ).distinct()


class WeatherData(models.Model):
    WEATHER_CONDITIONS = [
        ('sunny',  '☀️ Günəşli'),
        ('cloudy', '☁️ Buludlu'),
        ('rainy',  '🌧️ Yağmurlu'),
        ('stormy', '⛈️ Tufanlı'),
        ('foggy',  '🌫️ Dumanlı'),
        ('snowy',  '❄️ Qarlı'),
        ('windy',  '💨 Küləkli'),
    ]

    field        = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='weather_data')
    weather_date = models.DateField(verbose_name='Hava tarixi')

    temperature_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Maksimum temperatur (°C)')
    temperature_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Minimum temperatur (°C)')
    temperature_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Orta temperatur (°C)')

    humidity_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Orta hava rütubəti (%)')
    humidity_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Maks. hava rütubəti (%)')
    humidity_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Min. hava rütubəti (%)')

    precipitation_mm   = models.DecimalField(max_digits=8, decimal_places=2, null=True, verbose_name='Yağıntı (mm)')
    wind_speed_avg     = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name='Orta külək (m/s)')
    wind_speed_max     = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name='Maks. külək (m/s)')
    wind_direction_degrees  = models.IntegerField(null=True, blank=True, verbose_name='Külək istiqaməti (°)')
    solar_radiation_mj_m2   = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Günəş radiasiyası (MJ/m²)')
    evapotranspiration_mm   = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Evapotranspirasiya (mm)')

    weather_condition  = models.CharField(max_length=20, choices=WEATHER_CONDITIONS, verbose_name='Hava şəraiti')
    data_source        = models.CharField(max_length=50, default='api', verbose_name='Məlumat mənbəyi')
    forecast_accuracy  = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Proqnoz dəqiqliyi (%)')
    created_at         = models.DateTimeField(auto_now=True)

    objects = WeatherManager()

    class Meta:
        verbose_name        = 'Hava məlumatı'
        verbose_name_plural = 'Hava məlumatları'
        unique_together     = ['field', 'weather_date']
        ordering            = ['-weather_date']

    def __str__(self):
        return f"{self.field.name} – {self.weather_date} – {self.get_smart_condition_display()}"

    # ── Hesablama metodları ────────────────────────────────────────

    def is_rainy_day(self):
        return bool(self.precipitation_mm and self.precipitation_mm > 0)

    def is_windy_day(self):
        return bool(self.wind_speed_max and self.wind_speed_max > 10)

    def is_hot_day(self):
        return bool(self.temperature_max and self.temperature_max > 30)

    def is_cold_day(self):
        return bool(self.temperature_min and self.temperature_min < 5)

    def get_temperature_range(self):
        t_min = self.temperature_min or '—'
        t_max = self.temperature_max or '—'
        return f"{t_min}°C – {t_max}°C"

    # ── BUG DÜZƏLİŞ: weather_condition-u real dataya əsasən hesabla ──
    # utils.py yağıntılı günü "sunny" saxlaya bilir.
    # Bu metod DB-dəki condition deyil, real dəyərləri əsas götürür.
    def get_smart_condition(self):
        """
        DB-dəki weather_condition-a güvənmək əvəzinə real dəyərlərdən
        avtomatik şərait hesablayır.
        """
        prec  = float(self.precipitation_mm or 0)
        w_max = float(self.wind_speed_max    or 0)
        t_min = float(self.temperature_min   or 20)
        t_max = float(self.temperature_max   or 20)

        if prec > 20 or w_max > 20:
            return 'stormy'
        if t_min < 0 and prec > 2:
            return 'snowy'
        if prec > 5:
            return 'rainy'
        if prec > 0.5:
            return 'cloudy'
        if w_max > 10:
            return 'windy'
        if t_max < 5:
            return 'foggy'   # soyuq + quru → duman ehtimalı
        return 'sunny'

    def get_smart_condition_display(self):
        """Human-readable, emoji ilə"""
        icons = {
            'sunny':  '☀️ Günəşli',
            'cloudy': '⛅ Buludlu',
            'rainy':  '🌧️ Yağmurlu',
            'stormy': '⛈️ Tufanlı',
            'foggy':  '🌫️ Dumanlı',
            'snowy':  '❄️ Qarlı',
            'windy':  '💨 Küləkli',
        }
        return icons.get(self.get_smart_condition(), '⛅ Buludlu')

    def get_smart_condition_icon(self):
        """Yalnız emoji"""
        emojis = {
            'sunny': '☀️', 'cloudy': '⛅', 'rainy': '🌧️',
            'stormy': '⛈️', 'foggy': '🌫️', 'snowy': '❄️', 'windy': '💨',
        }
        return emojis.get(self.get_smart_condition(), '⛅')

    def get_weather_risk_level(self):
        prec  = float(self.precipitation_mm or 0)
        w_max = float(self.wind_speed_max    or 0)
        if prec > 50 or w_max > 20:
            return 'high'
        if prec > 10 or w_max > 12:
            return 'medium'
        return 'low'

    def get_weather_risk_display(self):
        labels = {'high': '🔴 Yüksək', 'medium': '🟡 Orta', 'low': '🟢 Aşağı'}
        return labels.get(self.get_weather_risk_level(), '🟢 Aşağı')

    @property
    def humidity_display(self):
        """
        Template-də həmişə get_smart_condition_display() işlət,
        humidity_avg isə HAVA rütubətidir — torpaq nəmliyi deyil.
        """
        if self.humidity_avg is None:
            return '—'
        return f"{self.humidity_avg}%"
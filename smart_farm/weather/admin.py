
from django.contrib import admin
from .models import WeatherData

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['field', 'weather_date', 'temperature_avg', 'humidity_avg', 
                   'precipitation_mm', 'weather_condition', 'data_source']
    list_filter = ['weather_date', 'weather_condition', 'data_source', 'field']
    search_fields = ['field__name']
    date_hierarchy = 'weather_date'
    
    fieldsets = (
        ('Əsas Məlumatlar', {
            'fields': ('field', 'weather_date', 'weather_condition', 'data_source')
        }),
        ('Temperatur', {
            'fields': ('temperature_min', 'temperature_max', 'temperature_avg'),
            'classes': ('collapse',)
        }),
        ('Rütubət', {
            'fields': ('humidity_min', 'humidity_max', 'humidity_avg'),
            'classes': ('collapse',)
        }),
        ('Digər Parametrlər', {
            'fields': ('precipitation_mm', 'wind_speed_avg', 'wind_speed_max',
                      'wind_direction_degrees', 'solar_radiation_mj_m2', 
                      'evapotranspiration_mm', 'forecast_accuracy'),
            'classes': ('collapse',)
        }),
    )
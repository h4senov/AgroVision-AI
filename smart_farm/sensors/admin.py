from django.contrib import admin
from .models import Sensor

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['name', 'sensor_type', 'field', 'is_active']
    list_filter = ['sensor_type', 'is_active']

 
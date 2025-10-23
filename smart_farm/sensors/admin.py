from django.contrib import admin
from .models import Sensor, SensorData


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['name', 'sensor_code', 'sensor_type', 'field', 'battery_level', 'is_active', 'user']
    list_filter = ['sensor_type', 'is_active', 'installation_date']
    search_fields = ['name', 'sensor_code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active', 'battery_level']
    
    fieldsets = (
        ('Əsas Məlumatlar', {
            'fields': ('field', 'user', 'name', 'sensor_code', 'sensor_type', 'description')
        }),
        ('Yerləşmə', {
            'fields': ('installation_date', 'latitude', 'longitude')
        }),
        ('Status', {
            'fields': ('battery_level', 'data_interval', 'is_active', 'last_maintenance')
        }),
        ('Sistem', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'value', 'unit', 'recorded_at']
    list_filter = ['sensor__sensor_type', 'recorded_at']
    search_fields = ['sensor__name', 'sensor__sensor_code']
    readonly_fields = ['recorded_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(sensor__user=request.user)
from django.contrib import admin
from .models import Plant

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ['plant_type', 'field', 'planting_date', 'growth_stage', 'status', 'user']
    list_filter = ['plant_type', 'growth_stage', 'status', 'planting_date']
    search_fields = ['variety', 'field__name', 'notes']
    date_hierarchy = 'planting_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Əsas Məlumatlar', {
            'fields': ('field', 'user', 'plant_type', 'variety')
        }),
        ('Vaxtlar', {
            'fields': ('planting_date', 'expected_harvest_date', 'actual_harvest_date')
        }),
        ('Status', {
            'fields': ('growth_stage', 'status', 'area_hectares')
        }),
        ('Qeydlər', {
            'fields': ('notes',)
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
from django.contrib import admin
from .models import Vacancy, Application

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'location', 'is_active', 'created_at')
    list_filter = ('is_active', 'department')
    search_fields = ('title', 'description')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'vacancy', 'email', 'created_at', 'reviewed')
    list_filter = ('reviewed', 'created_at')
    search_fields = ('name', 'email', 'vacancy__title')
    readonly_fields = ('created_at',) # Dəyişdirilə bilməz
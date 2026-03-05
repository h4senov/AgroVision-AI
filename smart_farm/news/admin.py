from django.contrib import admin
from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display    = ('title', 'is_published', 'created_at')
    list_filter     = ('is_published',)
    search_fields   = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}   # slug avtomatik doldurulur
    list_editable   = ('is_published',)
    ordering        = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Əsas Məlumat', {
            'fields': ('title', 'slug', 'image', 'is_published')
        }),
        ('Məzmun', {
            'fields': ('content',)
        }),
        ('Tarix', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
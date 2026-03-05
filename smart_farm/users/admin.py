from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# Register your models here.

admin.site.register(CustomUser,UserAdmin)

from .models import UserSession

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'country', 'last_login', 'user_agent')
    list_filter  = ('country',)
    search_fields = ('user__username', 'ip_address')
    ordering = ('-last_login',)
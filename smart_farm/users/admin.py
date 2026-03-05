from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserSession

# CustomUser Admini
admin.site.register(CustomUser, UserAdmin)

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    # Cədvəldə hansı sütunlar görünsün
    list_display = ('get_user_status', 'display_user', 'ip_address', 'country_city', 'device_info', 'last_login_formatted')
    
    # Sağ tərəfdəki filtrlər
    list_filter = ('user__role', 'country', 'device', 'is_bot', 'created_at')
    
    # Axtarış sahəsi
    search_fields = ('user__username', 'ip_address', 'city', 'user__phone')
    
    # --- Xüsusi Sütun Funksiyaları ---

    def get_user_status(self, obj):
        if not obj.user:
            return format_html('<span style="color: #666;">🔍 Anonim Qonaq</span>')
        
        # Roluna görə rənglər
        colors = {
            'admin': '#d9534f',   # Qırmızı
            'farmer': '#5cb85c',  # Yaşıl
            'expert': '#5bc0de',  # Mavi
            'guest': '#f0ad4e',   # Narıncı
        }
        role_name = dict(CustomUser.ROLE_CHOICES).get(obj.user.role, "Bilinmir")
        color = colors.get(obj.user.role, "#777")
        
        return format_html(
            '<strong style="color: {};">{}</strong>',
            color, role_name
        )
    get_user_status.short_description = 'İstifadəçi Tipi'

    def display_user(self, obj):
        if obj.user:
            return f"{obj.user.username} ({obj.user.get_full_name()})"
        return obj.ip_address
    display_user.short_description = 'İstifadəçi / IP'

    def country_city(self, obj):
        return f"{obj.country} / {obj.city}" if obj.country else "Məlum deyil"
    country_city.short_description = 'Məkan'

    def device_info(self, obj):
        icon = "📱" if obj.device == "Mobile" else "💻"
        return f"{icon} {obj.browser} ({obj.os})"
    device_info.short_description = 'Cihaz/Brauzer'

    # Xətanı düzəldən hissə: last_activity -> last_login
    def last_login_formatted(self, obj):
        if obj.last_login:
            return obj.last_login.strftime("%d.%m.%Y %H:%M")
        return "-"
    last_login_formatted.short_description = 'Son Giriş'
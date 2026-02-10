from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns # Bu vacibdir

# 1. Dil dəyişmə funksiyası (prefixsiz qalır)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# 2. Bütün digər səhifələr dil prefixi (məs: /az/dashboard/) alır
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('users/', include('users.urls', namespace='users')),
    path('fields/', include('fields.urls', namespace='fields')),
    path('plants/', include('plants.urls', namespace='plants')),
    path('sensors/', include('sensors.urls', namespace='sensors')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('weather/', include('weather.urls', namespace='weather')),   
    path('irrigation/', include('irrigation.urls', namespace='irrigation')),
   
    path('careers/', include('careers.urls')),
    path('news/', include('news.urls')),
    path('products/', include('products.urls')),
    path('info/', include('pages.urls')),
    
    
    # prefix_default_language=False 
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
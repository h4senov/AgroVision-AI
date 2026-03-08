from django.urls import path
from . import views

app_name = 'core' 

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/live-stats/', views.live_stats_api, name='live_stats_api'),
]
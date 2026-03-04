from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.WeatherDataListView.as_view(), name='weather_list'),
    path('<int:pk>/', views.WeatherDataDetailView.as_view(), name='weather_detail'),
    path('<int:pk>/edit/', views.WeatherDataUpdateView.as_view(), name='weather_edit'),
    path('<int:pk>/delete/', views.WeatherDataDeleteView.as_view(), name='weather_delete'),
    path('sync/', views.sync_weather, name='sync_weather'),
]
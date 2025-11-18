from django.urls import path
from . import views


template_name = 'weather/weather_form.html'
app_name = 'weather'  
urlpatterns = [
    path('', views.WeatherDataListView.as_view(), name='weather_list'),
    path('<int:pk>/', views.WeatherDataDetailView.as_view(), name='weather_detail'),
    path('add/', views.WeatherDataCreateView.as_view(), name='weather_form'),
    path('<int:pk>/edit/', views.WeatherDataUpdateView.as_view(), name='weather_edit'),
    path('<int:pk>/delete/', views.WeatherDataDeleteView.as_view(), name='weather_delete'),
]
from django.urls import path
from . import views


urlpatterns = [
    path('', views.sensor_list, name='sensor_list'),
    path('<int:sensor_id>/', views.sensor_detail, name='sensor_detail'),
    path('add/', views.add_sensor, name='add_sensor'),
    path('<int:sensor_id>/edit/', views.edit_sensor, name='edit_sensor'),
    path('<int:sensor_id>/delete/', views.delete_sensor, name='delete_sensor'),
]
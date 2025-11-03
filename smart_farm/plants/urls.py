from django.urls import path
from . import views
app_name = 'plants'

urlpatterns = [
    path('', views.plant_list, name='plant_list'),
    path('<int:plant_id>/', views.plant_detail, name='plant_detail'),
    path('add/', views.add_plant, name='add_plant'),
    path('<int:plant_id>/edit/', views.edit_plant, name='edit_plant'),
    path('<int:plant_id>/delete/', views.delete_plant, name='delete_plant'),
]
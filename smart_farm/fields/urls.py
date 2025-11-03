from django.urls import path
from . import views

app_name = 'fields'
urlpatterns = [
    path('',views.field_list, name='field_list'),
    path('<int:field_id>/', views.field_detail, name='field_detail'),
    path('add/', views.add_field, name='add_field'),
    path('<int:field_id>/edit/', views.edit_field, name='edit_field'),
    path('<int:field_id>/delete/', views.delete_field, name='delete_field')
]   

from django.urls import path
from . import views


app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('status/', views.get_inventory_status, name='status'),
     path('low-stock/', views.check_low_stock, name='low_stock'),
    path('add/', views.add_inventory, name='add_inventory'),
    path('<int:item_id>/', views.inventory_detail, name='inventory_detail'),
    path('<int:item_id>/edit/', views.edit_inventory, name='edit_inventory'),
    path('<int:item_id>/delete/', views.delete_inventory, name='delete_inventory'),
    path('<int:item_id>/track-usage/', views.track_inventory_usage, name='track_usage'),
]

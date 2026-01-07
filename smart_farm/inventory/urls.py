from django.urls import path
from . import views
from .views import (
    InventoryListView,
    InventoryDetailView, 
    InventoryCreateView,
    InventoryUpdateView,
    InventoryDeleteView,
    get_inventory_status,
    track_inventory_usage,
    low_stock
)

app_name = 'inventory'

urlpatterns = [
     
    path('', InventoryListView.as_view(), name='inventory_list'),
    path('add/', InventoryCreateView.as_view(), name='add_inventory'),
    path('<int:pk>/', InventoryDetailView.as_view(), name='inventory_detail'),
    path('<int:pk>/edit/', InventoryUpdateView.as_view(), name='edit_inventory'),
    path('<int:pk>/delete/', InventoryDeleteView.as_view(), name='delete_inventory'),
    
     
    path('status/', views.get_inventory_status, name='get_inventory_status'),
    path('low-stock/', views.low_stock, name='low_stock'),
    path('track-usage/<int:item_id>/', views.track_inventory_usage, name='track_inventory_usage'),
]
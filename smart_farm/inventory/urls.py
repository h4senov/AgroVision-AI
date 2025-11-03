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
    # Generic Views
    path('', InventoryListView.as_view(), name='inventory_list'),
    path('add/', InventoryCreateView.as_view(), name='add_inventory'),
    path('<int:pk>/', InventoryDetailView.as_view(), name='inventory_detail'),
    path('<int:pk>/edit/', InventoryUpdateView.as_view(), name='edit_inventory'),
    path('<int:pk>/delete/', InventoryDeleteView.as_view(), name='delete_inventory'),
    
    # Function-based Views (xüsusi məntiq)
    path('status/', get_inventory_status, name='inventory_status'),
    path('<int:item_id>/track-usage/', track_inventory_usage, name='track_usage'),
    path('low-stock/', views.low_stock, name='low_stock'),
]
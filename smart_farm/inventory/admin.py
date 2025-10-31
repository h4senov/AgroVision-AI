from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    
    list_display = ['item_code', 'item_name', 'category', 'quantity', 'unit', 'stock_status_display']
    list_filter = ['category', 'created_at']
    search_fields = ['item_name', 'item_code', 'supplier_name']
    
    def stock_status_display(self, obj):
        """Stok statusunu rəngli göstər"""
        status = obj.stock_status()
        if status == 'low':
            return '🔴 Aşağı'
        elif status == 'normal':
            return '🟢 Normal' 
        else:
            return '🟡 Yüksək'
    stock_status_display.short_description = 'Stok Statusu'
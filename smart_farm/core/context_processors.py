from django.db.models import Count, Sum
from fields.models import Field
from plants.models import Plant
from sensors.models import Sensor
from inventory.models import Inventory

def farm_stats(request):
    """
    🚜 FARM STATISTICS - Bütün səhifələrə ferma statistikalarını ötürür
    🎯 ÖYRƏNİRİK: Context Processors yaratmaq və istifadə etmək
    """
    
    # Əgər user authenticated deyilsə, boş context qaytar
    if not request.user.is_authenticated:
        return {
            'total_fields': 0,
            'total_plants': 0,
            'total_sensors': 0,
            'total_inventory': 0,
            'low_stock_count': 0,
        }
    
    # Statistikaları hesabla
    total_fields = Field.objects.filter(user=request.user).count()
    total_plants = Plant.objects.filter(user=request.user).count()
    total_sensors = Sensor.objects.filter(user=request.user).count()
    total_inventory = Inventory.objects.filter(user=request.user).count()
    
    # Aşağı stokda olan məhsullar
    user_inventory = Inventory.objects.filter(user=request.user)
    low_stock_count = len([item for item in user_inventory if item.stock_status() == 'low'])
    
    # Context qaytar
    return {
        'total_fields': total_fields,
        'total_plants': total_plants, 
        'total_sensors': total_sensors,
        'total_inventory': total_inventory,
        'low_stock_count': low_stock_count,
        'farm_stats_available': True,  # ⭐ Template-də yoxlamaq üçün
    }

def user_profile(request):
    """
    👤 USER PROFILE - Bütün səhifələrə user məlumatlarını ötürür
    """
    if not request.user.is_authenticated:
        return {}
    
    return {
        'current_user': request.user,
        'user_farm_name': request.user.farm_name or "Fermam",
    }
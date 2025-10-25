from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from fields.models import Field
from plants.models import Plant
from sensors.models import Sensor
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

def home(request):
    if request.user.is_authenticated:
        total_fields = Field.objects.filter(user=request.user).count()
        total_plants = Plant.objects.filter(user=request.user).count()
    else:
        total_fields = 0
        total_plants = 0
    
    context = {
        'total_fields': total_fields,
        'total_plants': total_plants,
    }
    return render(request, 'core/home.html', context)

@login_required
def dashboard(request):
    # Fields
    fields = Field.objects.filter(user=request.user)
    total_fields = fields.count()
    total_farm_area = fields.aggregate(total=Sum('area_hectares'))['total'] or 0
    
    # Plants
    plants = Plant.objects.filter(user=request.user)
    total_plants = plants.count()
    total_plant_area = plants.aggregate(total=Sum('area_hectares'))['total'] or 0
    active_plants_count = plants.filter(status='active').count()
    
    # Upcoming harvests
    next_week = timezone.now().date() + timedelta(days=7)
    upcoming_harvests = plants.filter(
        status='active',
        expected_harvest_date__lte=next_week,
        expected_harvest_date__gte=timezone.now().date()
    ).count()
    
    # Sensors
    sensors = Sensor.objects.filter(user=request.user)
    total_sensors = sensors.count()
    active_sensors = sensors.filter(is_active=True).count()
    
    # Recent plants for activity
    recent_plants = plants.order_by('-created_at')[:5]
    
    # Plant distribution
    plant_distribution = plants.values('plant_type').annotate(
        count=Count('id'),
        total_area=Sum('area_hectares')
    ).order_by('-count')
    
    context = {
        'total_fields': total_fields,
        'total_plants': total_plants,
        'total_sensors': total_sensors,
        'active_sensors': active_sensors,
        'total_farm_area': total_farm_area,
        'total_plant_area': total_plant_area,
        'active_plants_count': active_plants_count,
        'upcoming_harvests': upcoming_harvests,
        'recent_plants': recent_plants,
        'plant_distribution': plant_distribution,
    }
    
    return render(request, 'core/dashboard.html', context)
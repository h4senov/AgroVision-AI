from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from fields.models import Field
from plants.models import Plant
from sensors.models import Sensor
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from weather.models import WeatherData

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

    
    
    week_ago = timezone.now().date() - timedelta(days=7)
    recent_weather = WeatherData.objects.filter(
        field__user=request.user, 
        weather_date__gte=week_ago
    ).order_by('-weather_date')[:5]

    # Field metrics üçün nümunə
    sample_field = fields.first()
    field_metrics = None
    if sample_field:
        field_metrics = Field.objects.calculate_field_metrics(sample_field.id)

    # Plant predictions
    upcoming_plants = plants.filter(status='active')[:3]
    plant_predictions = {}
    for plant in upcoming_plants:
        plant_predictions[plant.id] = Plant.objects.predict_harvest_time(plant.id)



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
        'recent_weather': recent_weather,
        'field_metrics': field_metrics,
        'plant_predictions': plant_predictions,
    }
    
    return render(request, 'core/dashboard.html', context)
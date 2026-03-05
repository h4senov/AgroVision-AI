from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import  Sum, F, Q, Count
from django.utils import timezone
from datetime import timedelta

 
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from irrigation.models import IrrigationSchedule
from plants.models import Plant
from sensors.models import Sensor
from fields.models import Field
from weather.models import WeatherData

def home(request):
    context = {}

    if request.user.is_authenticated:
        user = request.user
        today = timezone.now().date()

        # Sahə nəmliyi: son suvarma və ya ortalama dəyər
        last_moisture = IrrigationSchedule.objects.filter(
            field__user=user
        ).order_by('-irrigation_date').first()

        if last_moisture:
            field_moisture = last_moisture.soil_moisture_level
        else:
            field_moisture = 15  # Default dəyər

        # AI mesajı (dashboard-dan götürülən logic)
        critical_field = IrrigationSchedule.objects.filter(
            field__user=user,
            soil_moisture_level__lt=20
        ).order_by('-irrigation_date').first()

        if critical_field:
            ai_message = f"{critical_field.field.name} sahəsində rütubət {critical_field.soil_moisture_level}% düşüb. Bitki təhlükədədir!"
        else:
            ai_message = "Sistem stabil işləyir, kritik vəziyyət aşkarlanmadı."

        context.update({
            'field_moisture': field_moisture,
            'ai_message': ai_message
        })

    return render(request, 'core/home.html', context)


from irrigation.models import IrrigationSchedule
from inventory.models import Inventory

@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()
    
    # 1. Real Statistikalar
    total_fields = user.fields.count()
    total_plants = user.fields.filter(plants__isnull=False).distinct().count()
    total_sensors = user.fields.aggregate(Count('sensors'))['sensors__count'] or 0

    from weather.models import WeatherData
    temp_data = WeatherData.objects.filter(field__user=user).order_by('weather_date')[:6]
    chart_temp_labels = [d.weather_date.strftime('%H:%M') for d in temp_data]
    chart_temp_values = [float(d.temperature_max) for d in temp_data]

    latest_weather = WeatherData.objects.filter(field__user=user).order_by('-weather_date').first()

    ph_optimal = user.fields.filter(ph_level__gte=6.5, ph_level__lte=7.5).count()
    ph_acidic = user.fields.filter(ph_level__lt=6.5).count()
    ph_alkaline = user.fields.filter(ph_level__gt=7.5).count()

    # Su Sərfiyyatı (Yalnız tamamlanmış və bugünkü)
    water_usage = IrrigationSchedule.objects.filter(
        field__user=user, 
        status='completed',
        irrigation_date=today
    ).aggregate(Sum('water_volume_liters'))['water_volume_liters__sum'] or 0

    # 2. Növbəti Suvarmalar (Bazadan real gələn planlar)
    upcoming_irrigations = IrrigationSchedule.objects.filter(
        field__user=user,
        status='planned',
        irrigation_date__gte=today
    ).order_by('irrigation_date', 'start_time')[:5]

    # 3. Anbar Xəbərdarlığı (Real kritik stok)
    # Kritik səviyyəsi 10-dan aşağı olan mallar
    low_stock_items = Inventory.objects.filter(user=user, quantity__lt=10)[:3]

    # 4. Dinamik AI Mesajı (Real data analizi)
    # Son suvarma qeydində rütubəti 20-dən aşağı olan sahə varmı?
    critical_field = IrrigationSchedule.objects.filter(
        field__user=user, 
        soil_moisture_level__lt=20
    ).order_by('-irrigation_date').first()

    if critical_field:
        ai_msg = {
            'title': 'Təcili Müdaxilə!',
            'text': f"{critical_field.field.name} sahəsində rütubət {critical_field.soil_moisture_level}%-ə düşüb. Bitki təhlükədədir!",
            'type': 'danger', 'icon': 'fa-exclamation-triangle'
        }
    elif low_stock_items.exists():
        ai_msg = {
            'title': 'Anbar xəbərdarlığı',
            'text': f"Anbarda {low_stock_items.first().item_name} bitmək üzrədir. Tədarük planlayın.",
            'type': 'warning', 'icon': 'fa-boxes'
        }
    else:
        ai_msg = {
            'title': 'Hər şey qaydasındadır',
            'text': 'Sistem stabil işləyir, kritik bir vəziyyət aşkarlanmadı.',
            'type': 'success', 'icon': 'fa-check-circle'
        }

    recent_activities = IrrigationSchedule.objects.filter(field__user=user).order_by('-irrigation_date')[:3]
     

    context = {
        'total_fields': total_fields,
        'total_plants': total_plants,
        'water_usage': water_usage,
        'total_sensors': total_sensors,
        'upcoming_irrigations': upcoming_irrigations,
        'low_stock_items': low_stock_items,
        'ai_msg': ai_msg,
        'latest_weather': latest_weather,
        'chart_temp_labels': chart_temp_labels,
        'chart_temp_values': chart_temp_values,
        'ph_dist': [ph_optimal, ph_acidic, ph_alkaline],
        'recent_activities': recent_activities,
        'fields':       Field.objects.filter(user=request.user),
        'plants':       Plant.objects.filter(field__user=request.user, status='active'),
        'sensors':      Sensor.objects.filter(field__user=request.user),
        'weather_list': WeatherData.objects.filter(field__user=request.user).order_by('-created_at')[:9],
        
    }
    return render(request, 'core/dashboard.html', context)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Q, Count
from django.utils import timezone
from datetime import timedelta

 
def home(request):
    """
    Landing Page: Layihənin məqsədini, qlobal statistikaları və animasiyalı təqdimatı göstərir.
    User login olsa belə, bura ana səhifə kimi görünür, amma "Dashboarda Keç" düyməsi olur.
    """
    # Bu rəqəmlər saytın ümumi "gücünü" göstərmək üçün marketinq məqsədlidir (simulyasiya)
    # Reallıqda bütün userlərin cəmini hesablaya bilərsən.
    context = {
        'global_water_saved': 15400,  # Tonla
        'global_active_sensors': 450,
        'global_ai_analysis': 12000,
        'farmers_count': 85
    }
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

    # 5. Son Hava Məlumatı (Ən son hansı sahəyə hava daxil edilibsə)
    # Bu hissə sənin WeatherData modelindən gəlir
    from weather.models import WeatherData # Modelin adını dəqiqləşdir
    latest_weather = WeatherData.objects.filter(field__user=user).order_by('-weather_date').first()

    context = {
        'total_fields': total_fields,
        'total_plants': total_plants,
        'water_usage': water_usage,
        'total_sensors': total_sensors,
        'upcoming_irrigations': upcoming_irrigations,
        'low_stock_items': low_stock_items,
        'ai_msg': ai_msg,
        'latest_weather': latest_weather,
    }
    return render(request, 'core/dashboard.html', context)
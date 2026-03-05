from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from irrigation.models import IrrigationSchedule
from inventory.models import Inventory
from plants.models import Plant
from sensors.models import Sensor
from fields.models import Field
from users.views import get_client_ip
from users.models import UserSession
from weather.models import WeatherData

from news.models import News   # ← faylın yuxarısına əlavə et (digər import-ların yanına)


def home(request):

    # 1. QONAQ DATASINI TUTMAQ
    client_ip = get_client_ip(request)
    u_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
    
    # Giriş edibsə user-i götür, etməyibsə None (qonaq) qalsın
    curr_user = request.user if request.user.is_authenticated else None

    # Eyni qonaq səhifəni hər dəfə refresh edəndə bazanı doldurmasın deyə
    # IP və User-ə görə son girişi yeniləyirik (və ya .create istifadə et)
    UserSession.objects.update_or_create(
        ip_address=client_ip,
        user=curr_user,
        defaults={
            'user_agent': u_agent,
            'last_login': timezone.now(),
            'city': "Baku (Guest)", # Statikdir, GeoIP ilə dəyişmək olar
            'device': "Mobile" if "Mobile" in u_agent else "Desktop",
            'browser': u_agent.split(' ')[0] if u_agent else "Unknown"
        }
    )
     
    context = {
        'latest_news': News.objects.filter(is_published=True)[:3]
    }

    if request.user.is_authenticated:
        user = request.user
        last_moisture = IrrigationSchedule.objects.filter(
            field__user=user
        ).order_by('-irrigation_date').first()
        field_moisture = last_moisture.soil_moisture_level if last_moisture else 15

        critical_field = IrrigationSchedule.objects.filter(
            field__user=user, soil_moisture_level__lt=20
        ).order_by('-irrigation_date').first()

        ai_message = (
            f"{critical_field.field.name} sahəsində torpaq nəmliyi "
            f"{critical_field.soil_moisture_level}% düşüb. Suvarma tövsiyə edilir!"
            if critical_field
            else "Sistem stabil işləyir, kritik vəziyyət aşkarlanmadı."
        )
        context.update({
            'field_moisture': field_moisture,
            'ai_message':     ai_message,
        })

    return render(request, 'core/home.html', context)


@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    # ── Statistikalar ──────────────────────────────────────────
    total_fields  = Field.objects.filter(user=user).count()
    # BUG DÜZƏLİŞ: əvvəl sahə sayırdı, indi bitki sayır
    total_plants  = Plant.objects.filter(field__user=user).count()
    total_sensors = Sensor.objects.filter(field__user=user).count()

    # ── Su sərfiyyatı ──────────────────────────────────────────
    water_usage = IrrigationSchedule.objects.filter(
        field__user=user,
        status='completed',
        irrigation_date=today
    ).aggregate(Sum('water_volume_liters'))['water_volume_liters__sum'] or 0

    # ── pH paylanması ──────────────────────────────────────────
    ph_optimal  = Field.objects.filter(user=user, ph_level__gte=6.5, ph_level__lte=7.5).count()
    ph_acidic   = Field.objects.filter(user=user, ph_level__lt=6.5).count()
    ph_alkaline = Field.objects.filter(user=user, ph_level__gt=7.5).count()

    # ── Hava qrafikləri ───────────────────────────────────────
    temp_data = (
        WeatherData.objects
        .filter(field__user=user, weather_date__gte=today - timedelta(days=6))
        .values('weather_date')                         # tarix üzrə qruplaşdır
        .annotate(
            avg_temp_max=Avg('temperature_max'),        # bütün sahələrin ortalaması
            avg_temp_min=Avg('temperature_min'),
            avg_humidity=Avg('humidity_avg'),
        )
        .order_by('weather_date')
    )
    chart_temp_labels  = [d['weather_date'].strftime('%d %b') for d in temp_data]
    chart_temp_values  = [round(float(d['avg_temp_max'] or 0), 1)  for d in temp_data]
    chart_temp_min     = [round(float(d['avg_temp_min'] or 0), 1)  for d in temp_data]
    chart_humidity     = [round(float(d['avg_humidity'] or 0), 1)  for d in temp_data]

    # ── Son hava məlumatı ──────────────────────────────────────
    latest_weather = (
        WeatherData.objects
        .filter(field__user=user)
        .order_by('-weather_date', '-created_at')
        .first()
    )

    # ── Növbəti suvarmalar ─────────────────────────────────────
    upcoming_irrigations = (
        IrrigationSchedule.objects
        .filter(field__user=user, status='planned', irrigation_date__gte=today)
        .select_related('field')
        .order_by('irrigation_date', 'start_time')[:8]
    )

    # ── Anbar xəbərdarlıqları ──────────────────────────────────
    low_stock_items = Inventory.objects.filter(user=user, quantity__lt=10)[:5]

    # ── AI mesajı ─────────────────────────────────────────────
    # BUG DÜZƏLİŞ: "torpaq nəmliyi" ilə "hava rütubəti"ni aydın ayırırıq
    critical_field = (
        IrrigationSchedule.objects
        .filter(field__user=user, soil_moisture_level__lt=20)
        .order_by('-irrigation_date')
        .first()
    )
    # Bugünkü havanın rütubəti (ayrıca — hava nəmliyi)
    today_humidity = (
        WeatherData.objects
        .filter(field__user=user, weather_date=today)
        .aggregate(avg=Avg('humidity_avg'))['avg']
    )

    if critical_field:
        ai_msg = {
            'title': '🌱 Torpaq quruyur — Suvarma lazımdır!',
            'text': (
                f"«{critical_field.field.name}» sahəsində torpaq nəmliyi "
                f"{critical_field.soil_moisture_level}%-ə düşüb "
                f"(hava rütubəti: {round(float(today_humidity), 0) if today_humidity else '—'}%). "
                f"Suvarma planı qurun."
            ),
            'type': 'danger', 'icon': 'fa-exclamation-triangle'
        }
    elif low_stock_items.exists():
        ai_msg = {
            'title': '📦 Anbar xəbərdarlığı',
            'text': f"«{low_stock_items.first().item_name}» bitmək üzrədir. Tədarük planlayın.",
            'type': 'warning', 'icon': 'fa-boxes'
        }
    else:
        ai_msg = {
            'title': '✅ Hər şey qaydasındadır',
            'text': 'Sistem stabil işləyir. Kritik vəziyyət aşkarlanmadı.',
            'type': 'success', 'icon': 'fa-check-circle'
        }

    # ── Sahə/bitki/sensor/hava listiləri (dashboard tabları üçün) ──
    fields       = Field.objects.filter(user=user).prefetch_related('plants')
    plants       = Plant.objects.filter(field__user=user).select_related('field')
    sensors      = Sensor.objects.filter(field__user=user).select_related('field')
    weather_list = (
        WeatherData.objects
        .filter(field__user=user)
        .select_related('field')
        .order_by('-weather_date')[:12]
    )

    # ── Suvarma statistikası ───────────────────────────────────
    today_consumption  = water_usage
    active_zones_count = IrrigationSchedule.objects.filter(
        field__user=user, status='active'
    ).count()
    next_irrigation = upcoming_irrigations.first()

    context = {
        # Statistika kartları
        'total_fields':   total_fields,
        'total_plants':   total_plants,
        'water_usage':    water_usage,
        'total_sensors':  total_sensors,

        # Qrafik
        'chart_temp_labels': chart_temp_labels,
        'chart_temp_values': chart_temp_values,
        'chart_temp_min':    chart_temp_min,
        'chart_humidity':    chart_humidity,
        'ph_dist':           [ph_optimal, ph_acidic, ph_alkaline],

        # Hava
        'latest_weather': latest_weather,
        'weather_list':   weather_list,

        # Suvarma
        'upcoming_irrigations': upcoming_irrigations,
        'today_consumption':    today_consumption,
        'active_zones_count':   active_zones_count,
        'next_irrigation':      next_irrigation,

        # Anbar & AI
        'low_stock_items': low_stock_items,
        'ai_msg':          ai_msg,

        # Tab listiləri
        'fields':   fields,
        'plants':   plants,
        'sensors':  sensors,
    }
    return render(request, 'core/dashboard.html', context)
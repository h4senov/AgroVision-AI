from django.shortcuts import render
from irrigation.models import IrrigationSchedule
from users.views import get_client_ip
from users.models import UserSession
from news.models import News
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
from django.utils import timezone
from datetime import date


# ──────────────────────────────────────────────────────────
#  DASHBOARD
# ──────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    from fields.models      import Field
    from plants.models      import Plant
    from sensors.models     import Sensor
    from irrigation.models  import IrrigationSchedule
    from inventory.models   import Inventory
    from weather.models     import WeatherData

    user = request.user

    # ── Sahələr
    fields = Field.objects.filter(user=user).prefetch_related('plants')

    # ── Bitkilər (aktiv)
    plants = Plant.objects.filter(
        field__user=user, status='active'
    ).select_related('field').order_by('-planting_date')

    # ── Sensorlar
    sensors = Sensor.objects.filter(
        field__user=user
    ).select_related('field').order_by('-is_active', 'name')

    # ── Suvarmalar (gələcək planlar)
    upcoming_irrigations = IrrigationSchedule.objects.filter(
        field__user=user,
        irrigation_date__gte=date.today()
    ).select_related('field').order_by('irrigation_date')[:6]

    # ── Anbar xəbərdarlıqları
    low_stock_items = Inventory.objects.filter(
        user=user, quantity__lte=10
    ).order_by('quantity')[:5]

    # ── Hava (bütün sahələrin ən son qeydi)
    weather_list = WeatherData.objects.filter(
        field__user=user
    ).order_by('-weather_date').distinct()[:3]

    latest_weather = weather_list.first()

    # ── Su istifadəsi (bugün)
    from django.db.models import Sum
    water_today = IrrigationSchedule.objects.filter(
        field__user=user,
        irrigation_date=date.today(),
        status='completed'
    ).aggregate(total=Sum('water_volume_liters'))['total'] or 0

    # ── pH paylanması (donut chart üçün)
    ph_values = fields.values_list('ph_level', flat=True)
    ph_dist   = _ph_distribution(ph_values)
    avg_ph    = round(sum(v for v in ph_values if v) / max(len([v for v in ph_values if v]), 1), 1)

    # ── AI mesajı
    ai_msg = _build_ai_msg(plants, low_stock_items, weather_list)

    return render(request, 'core/dashboard.html', {
        'fields':               fields,
        'plants':               plants,
        'sensors':              sensors,
        'upcoming_irrigations': upcoming_irrigations,
        'low_stock_items':      low_stock_items,
        'weather_list':         weather_list,
        'latest_weather':       latest_weather,
        'water_usage':          water_today,
        'total_fields':         fields.count(),
        'total_plants':         plants.count(),
        'total_sensors':        sensors.filter(is_active=True).count(),
        'ph_dist':              ph_dist,
        'avg_ph':               avg_ph,
        'ai_msg':               ai_msg,
        # grafik üçün
        'plant_health_rate':    _plant_health(plants),
        'irr_efficiency':       78,   # real hesablama əlavə edə bilərsiniz
    })


# ──────────────────────────────────────────────────────────
#  LIVE STATS API
#  GET /api/live-stats/   →  JSON
# ──────────────────────────────────────────────────────────
@login_required
def live_stats_api(request):
    from fields.models      import Field
    from plants.models      import Plant
    from sensors.models     import Sensor
    from irrigation.models  import IrrigationSchedule
    from inventory.models   import Inventory
    from weather.models     import WeatherData
    from django.db.models   import Sum

    user = request.user

    # ── Sahələr
    fields_count = Field.objects.filter(user=user).count()

    # ── Aktiv sensorlar
    sensors_active = Sensor.objects.filter(field__user=user, is_active=True).count()

    # ── Aktiv bitkilər
    plants_count = Plant.objects.filter(field__user=user, status='active').count()

    # ── Bugünkü su (tamamlanmış suvarmalar)
    water_today = IrrigationSchedule.objects.filter(
        field__user=user,
        irrigation_date=date.today(),
        status='completed'
    ).aggregate(t=Sum('water_volume_liters'))['t'] or 0

    # ── Anbar xəbərdarlığı sayı
    low_stock = Inventory.objects.filter(user=user, quantity__lte=10).count()

    # ── Ən son hava
    w = WeatherData.objects.filter(
        field__user=user
    ).order_by('-weather_date').first()

    if w:
        icon = '🌧️' if w.precipitation_mm > 0 else ('☀️' if w.temperature_max > 30 else '⛅')
        weather_str = f"{w.temperature_max}°C {icon}"
    else:
        weather_str = '—'

    return JsonResponse({
        'fields':         fields_count,
        'sensors_active': sensors_active,
        'plants':         plants_count,
        'water_today':    int(water_today),
        'low_stock':      low_stock,
        'weather':        weather_str,
    })


# ──────────────────────────────────────────────────────────
#  YARDIMÇI FUNKSİYALAR
# ──────────────────────────────────────────────────────────
def _ph_distribution(ph_values):
    """[optimal%, acid%, alkaline%] — donut chart üçün"""
    total  = len([v for v in ph_values if v])
    if not total:
        return [60, 25, 15]
    optimal  = sum(1 for v in ph_values if v and 6.0 <= v <= 7.5)
    acid     = sum(1 for v in ph_values if v and v < 6.0)
    alkaline = total - optimal - acid
    return [
        round(optimal  / total * 100),
        round(acid     / total * 100),
        round(alkaline / total * 100),
    ]


def _plant_health(plants):
    """Ortalama bitki sağlamlığı faizi"""
    healthy_stages = {'vegetative', 'flowering', 'fruiting'}
    total = plants.count()
    if not total:
        return 85
    healthy = plants.filter(growth_stage__in=healthy_stages).count()
    return round(healthy / total * 100)


def _build_ai_msg(plants, low_stock, weather_list):
    """Dashboard hero üçün AI mesajı"""
    # Yığıma hazır bitki
    harvest_ready = [p for p in plants if getattr(p, 'is_harvest_due', False)]
    if harvest_ready:
        return {
            'type':  'warning',
            'icon':  'fa-exclamation-triangle',
            'title': 'Yığıma hazır bitkilər var!',
            'text':  f"{len(harvest_ready)} bitki yığım mərhələsinədir. Sahəyə baxın.",
        }
    if low_stock.exists():
        return {
            'type':  'danger',
            'icon':  'fa-boxes',
            'title': 'Anbar xəbərdarlığı',
            'text':  f"{low_stock.count()} material tükənmək üzrədir.",
        }
    if weather_list:
        w = weather_list[0]
        if w.precipitation_mm > 10:
            return {
                'type':  'info',
                'icon':  'fa-cloud-rain',
                'title': 'Yağış gözlənilir',
                'text':  f"Suvarma planını uyğunlaşdırın — {w.precipitation_mm} mm proqnoz.",
            }
    return None
 

def log_user_session(request):
    """Sessiya məlumatlarını qeyd edən və MultipleObjectsReturned xətasını önləyən funksiya"""
    client_ip = get_client_ip(request)
    u_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
    curr_user = request.user if request.user.is_authenticated else None

    # filter() istifadə edirik ki, birdən çox nəticə gəlsə belə proqram çökməsin
    session_qs = UserSession.objects.filter(ip_address=client_ip, user=curr_user)

    if session_qs.exists():
        # Əgər varsa, ilk tapılanı yeniləyirik
        session = session_qs.first()
        session.user_agent = u_agent
        session.last_login = timezone.now()
        session.device = "Mobile" if "Mobile" in u_agent else "Desktop"
        session.browser = u_agent.split(' ')[0] if u_agent else "Unknown"
        session.save()
    else:
        # Yoxdursa, yeni qeyd yaradırıq
        UserSession.objects.create(
            ip_address=client_ip,
            user=curr_user,
            user_agent=u_agent,
            last_login=timezone.now(),
            city="Baku (Guest)",
            device="Mobile" if "Mobile" in u_agent else "Desktop",
            browser=u_agent.split(' ')[0] if u_agent else "Unknown"
        )

def home(request):

    log_user_session(request)
     
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
 
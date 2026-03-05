import requests
from datetime import date, timedelta
from django.utils import timezone


def get_coordinates(city_name):
    """Şəhər adından koordinat alır (Open-Meteo Geocoding API)"""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1, "language": "az"}
    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        if data.get("results"):
            r = data["results"][0]
            return r["latitude"], r["longitude"]
    except Exception:
        pass
    return None, None


# ── WMO Weather Interpretation Codes → bizim şərtlər ──────────────────
# https://open-meteo.com/en/docs#weathervariables
WMO_CONDITION_MAP = {
    0:  'sunny',   # Clear sky
    1:  'sunny',   # Mainly clear
    2:  'cloudy',  # Partly cloudy
    3:  'cloudy',  # Overcast
    45: 'foggy',   # Fog
    48: 'foggy',   # Icy fog
    51: 'rainy',   # Light drizzle
    53: 'rainy',   # Moderate drizzle
    55: 'rainy',   # Heavy drizzle
    56: 'snowy',   # Freezing drizzle
    57: 'snowy',
    61: 'rainy',   # Slight rain
    63: 'rainy',   # Moderate rain
    65: 'rainy',   # Heavy rain
    66: 'snowy',   # Freezing rain
    67: 'snowy',
    71: 'snowy',   # Slight snow
    73: 'snowy',
    75: 'snowy',   # Heavy snow
    77: 'snowy',   # Snow grains
    80: 'rainy',   # Slight showers
    81: 'rainy',   # Moderate showers
    82: 'rainy',   # Violent showers
    85: 'snowy',   # Snow showers
    86: 'snowy',
    95: 'stormy',  # Thunderstorm
    96: 'stormy',
    99: 'stormy',
}


def wmo_to_condition(code, wind_ms=0, precip=0):
    """
    WMO kodunu bizim şərtə çevirir.
    Kod yoxdursa yedək olaraq precip + wind ilə müəyyənləşdirir.
    """
    if code is not None and code in WMO_CONDITION_MAP:
        cond = WMO_CONDITION_MAP[code]
        # Günəşli amma güclü küləkdirsə → windy
        if wind_ms and wind_ms > 12 and cond == 'sunny':
            return 'windy'
        return cond

    # ── Yedək (WMO kodu gəlmədikdə) ──────────────────────────────
    p = precip  or 0
    w = wind_ms or 0

    if p > 20 or w > 18:  return 'stormy'
    if p > 3:              return 'rainy'   # BUG FIX: əvvəl >5 idi — 4.1mm qaçırdı
    if p > 0.5:            return 'cloudy'
    if w > 10:             return 'windy'
    return 'sunny'


def fetch_weather_for_field(field):
    """
    Field obyektini alıb hava datasını çəkir və DB-yə yazır.
    Son 7 gün + bugün (update_or_create).
    """
    from .models import WeatherData

    if not field.location:
        return None

    # ── Cache yoxlaması ─────────────────────────────────────────────
    last = WeatherData.objects.filter(
        field=field, weather_date=date.today()
    ).first()

    if last:
        # BUG FIX: .seconds → .total_seconds()
        # .seconds yalnız timedelta-nın 0–59 saniyelik hissəsini verir.
        # Məs: 2 saatın .seconds = 0, buna görə cache heç vaxt işləmirdi.
        elapsed = (timezone.now() - last.created_at).total_seconds()
        if elapsed < 3600:
            return 'cached'

    # ── Koordinatlar ────────────────────────────────────────────────
    lat, lon = get_coordinates(field.location)
    if not lat:
        return None

    today = date.today()
    start = today - timedelta(days=6)

    # ── Open-Meteo API ──────────────────────────────────────────────
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":  lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "windspeed_10m_max",
            "windspeed_10m_mean",
            "relative_humidity_2m_mean",
            "weathercode",                  # ← WMO kodu — dəqiq condition üçün
            "winddirection_10m_dominant",
        ],
        "timezone":   "Asia/Baku",
        "start_date": start.isoformat(),
        "end_date":   today.isoformat(),
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json().get("daily", {})
    except Exception:
        return None

    # ── Listiləri çək ───────────────────────────────────────────────
    dates        = data.get("time",                       [])
    temp_max     = data.get("temperature_2m_max",         [])
    temp_min     = data.get("temperature_2m_min",         [])
    temp_avg     = data.get("temperature_2m_mean",        [])
    precip       = data.get("precipitation_sum",          [])
    wind_max_kmh = data.get("windspeed_10m_max",          [])
    wind_avg_kmh = data.get("windspeed_10m_mean",         [])
    humidity     = data.get("relative_humidity_2m_mean",  [])
    wmo_codes    = data.get("weathercode",                [])
    wind_dir     = data.get("winddirection_10m_dominant", [])

    # km/h → m/s
    def to_ms(v):
        return round(v / 3.6, 1) if v is not None else None

    wind_max_ms = [to_ms(v) for v in wind_max_kmh]
    wind_avg_ms = [to_ms(v) for v in wind_avg_kmh]

    # ── DB-yə yaz ───────────────────────────────────────────────────
    saved = 0
    for i, d in enumerate(dates):
        p      = precip[i]      if i < len(precip)      else None
        w_max  = wind_max_ms[i] if i < len(wind_max_ms) else None
        w_code = wmo_codes[i]   if i < len(wmo_codes)   else None

        condition = wmo_to_condition(
            code    = int(w_code) if w_code is not None else None,
            wind_ms = float(w_max or 0),
            precip  = float(p     or 0),
        )

        WeatherData.objects.update_or_create(
            field        = field,
            weather_date = d,
            defaults={
                "temperature_max":        temp_max[i]    if i < len(temp_max)    else None,
                "temperature_min":        temp_min[i]    if i < len(temp_min)    else None,
                "temperature_avg":        temp_avg[i]    if i < len(temp_avg)    else None,
                "precipitation_mm":       p,
                "wind_speed_max":         w_max,
                "wind_speed_avg":         wind_avg_ms[i] if i < len(wind_avg_ms) else None,
                "humidity_avg":           humidity[i]    if i < len(humidity)    else None,
                "wind_direction_degrees": int(wind_dir[i]) if (i < len(wind_dir) and wind_dir[i] is not None) else None,
                "weather_condition":      condition,
                "data_source":            "open-meteo",
            }
        )
        saved += 1

    return saved
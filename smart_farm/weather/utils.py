import requests
from datetime import date, timedelta
from django.utils import timezone

def get_coordinates(city_name):
    """Şəhər adından koordinat alır"""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1, "language": "az"}
    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        if data.get("results"):
            r = data["results"][0]
            return r["latitude"], r["longitude"]
    except:
        pass
    return None, None

def fetch_weather_for_field(field):
    """Field obyektini alıb hava datasını çəkir və DB-yə yazır"""
    from .models import WeatherData

    if not field.location:
        return None

    last = WeatherData.objects.filter(
        field=field,
        weather_date=date.today()
    ).first()
    if last and (timezone.now() - last.created_at).seconds < 3600:
        return 'cached'

    lat, lon = get_coordinates(field.location)
    if not lat:
        return None

    today = date.today()
    start = today - timedelta(days=6)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
            "precipitation_sum", "windspeed_10m_max", "windspeed_10m_mean",
            "relative_humidity_2m_mean",   
        ],
        "timezone": "Asia/Baku",
        "start_date": start.isoformat(),
        "end_date": today.isoformat(),
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json().get("daily", {})
    except:
        return None

    dates      = data.get("time", [])
    temp_max   = data.get("temperature_2m_max", [])
    temp_min   = data.get("temperature_2m_min", [])
    temp_avg   = data.get("temperature_2m_mean", [])
    precip     = data.get("precipitation_sum", [])
    wind_max   = data.get("windspeed_10m_max", [])
    wind_avg   = data.get("windspeed_10m_mean", [])
    humidity   = data.get("relative_humidity_2m_mean", [])
    wind_max = [round(v / 3.6, 1) if v else v for v in wind_max]
    wind_avg = [round(v / 3.6, 1) if v else v for v in wind_avg]
    
    def get_condition(p, w):
        if p and p > 5: return "rainy"
        if w and w > 10: return "windy"
        return "sunny"

    for i, d in enumerate(dates):
        WeatherData.objects.update_or_create(
            field=field,
            weather_date=d,
            defaults={
                "temperature_max":  temp_max[i]  if i < len(temp_max)  else None,
                "temperature_min":  temp_min[i]  if i < len(temp_min)  else None,
                "temperature_avg":  temp_avg[i]  if i < len(temp_avg)  else None,
                "precipitation_mm": precip[i]    if i < len(precip)    else None,
                "wind_speed_max":   wind_max[i]  if i < len(wind_max)  else None,
                "wind_speed_avg":   wind_avg[i]  if i < len(wind_avg)  else None,
                "humidity_avg":     humidity[i]  if i < len(humidity)  else None,
                "weather_condition": get_condition(
                    precip[i]  if i < len(precip)  else None,
                    wind_max[i] if i < len(wind_max) else None
                ),
                "data_source": "open-meteo",
            }
        )
    return True
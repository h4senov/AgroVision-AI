from django.db import models
from django.utils import timezone
from django.db.models import Q, Avg, Sum
from django.conf import settings
from datetime import timedelta

class FieldManager(models.Manager):

    def search_fields(self, query, user, filters=None): 

        qs = self.filter(user=user)

        if query:
            qs = qs.filter(
                models.Q(name__icontains = query) 
            )
        if filters :   
            soil_type = filters.get('soil_type')
            min_area = filters.get('min_area')
            max_area = filters.get('max_area')
            irrigated = filters.get('irrigated')

            if soil_type:
                qs = qs.filter(soil_type=filters['soil_type'])
            if min_area:     
                qs = qs.filter(area_hectares__gte =filters['min_area'])
            if max_area:    
                qs = qs.filter(area_hectares__lte = filters['max_area']) 

            today = timezone.now().date()
            if irrigated == 'true':
                qs = qs.filter(
                    field_irrigation_records__isnull=False,
                    field_irrigation_records__irrigation_date__lt=timezone.now().date()
                ).distinct()
            elif irrigated == 'false':
                qs = qs.filter(
                    Q(field_irrigation_records__isnull=True) | 
                    Q(field_irrigation_records__irrigation_date__gte=today)).distinct()
          
        
        return qs

    def calculate_field_metrics(self, field_id):
        try:
            # Tek query-de her şeyi çekirik
            field = self.prefetch_related('plants', 'sensors', 'weather_data').get(id=field_id)

            # Bitki istatistikleri (Veritabanı seviyesinde count)
            plants = field.plants.all()
            total_plants = plants.count()
            active_plants = plants.filter(status='active').count()
            harvested_plants = plants.filter(status='harvested').count()

            # Sensor istatistikleri
            sensors = field.sensors.all()
            total_sensors = sensors.count()
            active_sensors = sensors.filter(is_active=True).count()
            
            # pH Analizi: 6.0 - 7.5 arası optimal sayılır
            ph = float(field.ph_level)
            ph_status = "Optimal"
            if ph < 6.0: ph_status = "Turşulu"
            elif ph > 7.5: ph_status = "Qələvili"

            base_score = self._calculate_field_health_score(field)
            if ph_status != "Optimal":
                base_score = round(base_score * 0.9, 2)


            # Hava durumu (Son 7 gün)
            week_ago = timezone.now().date() - timedelta(days=7)
            daily_weather = field.weather_data.filter(
                weather_date__gte=week_ago
            ).order_by('weather_date')

            weather_labels = [w.weather_date.strftime('%d %b') for w in daily_weather]
            weather_temps = [float(w.temperature_avg or 0) for w in daily_weather]
            
            # İstatistikleri mevcut daily_weather üzerinden alıyoruz (tekrar DB-ye gitmiyoruz)
            weather_stats = daily_weather.aggregate(
                avg_temp=Avg('temperature_avg'),
                total_precip=Sum('precipitation_mm')
            )

            return {
                'field_name': field.name,
                'total_area_hectares': float(field.area_hectares),
                'total_plants': total_plants,
                'active_plants': active_plants,
                'harvested_plants': harvested_plants,
                'plant_success_rate': round((harvested_plants / total_plants * 100), 2) if total_plants > 0 else 0,
                'total_sensors': total_sensors,
                'active_sensors': active_sensors,
                'sensor_health_rate': round((active_sensors / total_sensors * 100), 2) if total_sensors > 0 else 0,
                'avg_temperature_last_week': round(float(weather_stats['avg_temp'] or 0), 2),
                'total_precipitation_last_week': round(float(weather_stats['total_precip'] or 0), 2),
                'soil_type': field.get_soil_type_display(),
                'field_health_score': self._calculate_field_health_score(field),
                'weather_labels': weather_labels,
                'weather_temps': weather_temps, 
                'ph_level': field.ph_level,
                'ph_status': ph_status,
            }

        except self.model.DoesNotExist: 
            return {'error': 'Sahə tapılmadı'}   
        
    def _calculate_field_health_score(self, field):
         
        score = 100
        
         
        plants = field.plants.all()
        if plants.count() > 0:
            active_ratio = plants.filter(status='active').count() / plants.count()
            score *= active_ratio
        
         
        sensors = field.sensors.all()
        if sensors.count() > 0:
            active_sensor_ratio = sensors.filter(is_active=True).count() / sensors.count()
            score *= active_sensor_ratio
        
        
        from django.utils import timezone
        recent_weather = field.weather_data.filter(weather_date=timezone.now().date()).first()
        if recent_weather:
            if recent_weather.get_weather_risk_level() == 'high':
                score *= 0.7
            elif recent_weather.get_weather_risk_level() == 'medium':
                score *= 0.9
        
        return round(score, 2)      
    
    def is_irrigated(self):
        if self.field_irrigation_records.exists() and self.field_irrigation_records.first().irrigation_date < timezone.now().date():
            return True
        return False

class Field(models.Model):
    SOIL_TYPES = [
        ('sandy', 'Qumlu'),
        ('clay', 'Gil'),
        ('loamy', 'Humuslu'),
        ('silty', 'Limli'),
        ('peat', 'Torf'),
    ]

  
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)
    area_hectares = models.DecimalField(max_digits=10, decimal_places=2)
    soil_type = models.CharField(max_length=20, choices=SOIL_TYPES, default='loamy')
    ph_level = models.DecimalField(max_digits=3, decimal_places=1, default=7.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = FieldManager()
    def __str__(self):
        return self.name

    @property
    def last_irrigation(self):
        
        return self.field_irrigation_records.order_by('-irrigation_date').first()
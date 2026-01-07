from django.db import models
from users.models import CustomUser



    


class FieldManager(models.Manager):

    def search_fields(self, query, user, filters=None):

        qs = self.filter(user=user)

        if query:
            qs = qs.filter(
                models.Q(name__icontains = query) |
                models.Q(soil_type = query)
            )
        if filters :   
            soil_type = filters.get('soil_type')
            min_area = filters.get('min_area')
            max_area = filters.get('max_area')

            if soil_type:
                qs = qs.filter(soil_type=filters['soil_type'])
            if min_area:     
                qs = qs.filter(area_hectares__gte =filters['min_area'])
            if max_area:    
                qs = qs.filter(area_hectares__lte = filters['max_area']) 
        
        return qs

    def calculate_field_metrics(self, field_id):
        
        try:
            field =self.get(id=field_id)

            plants = field.plants.all()
            total_plants = plants.count()
            active_plants = plants.filter(status='active').count()
            harvested_plants = plants.filter(status='harvested').count()

            sensors = field.sensors.all()
            active_sensors = sensors.filter(is_active=True).count()
            from django.utils import timezone
            from datetime import timedelta

            week_ago = timezone.now().date() - timedelta(days=7)
            weather_data = field.weather_data.filter(weather_date__gte=week_ago)
            avg_temperature = weather_data.aggregate(avg_temp=models.Avg('temperature_avg'))['avg_temp']
            total_precipitation = weather_data.aggregate(total_precip=models.Sum('precipitation_mm'))['total_precip']

            metrics = {
                'field_name': field.name,
                'total_area_hectares': float(field.area_hectares),
                'total_plants': total_plants,
                'active_plants': active_plants,
                'harvested_plants': harvested_plants,
                'plant_success_rate': round((harvested_plants / total_plants * 100), 2) if total_plants > 0 else 0,
                'total_sensors': sensors.count(),
                'active_sensors': active_sensors,
                'sensor_health_rate': round((active_sensors / sensors.count() * 100), 2) if sensors.count() > 0 else 0,
                'avg_temperature_last_week': round(float(avg_temperature), 2) if avg_temperature else 0,
                'total_precipitation_last_week': round(float(total_precipitation), 2) if total_precipitation else 0,
                'soil_type': field.get_soil_type_display(),
                'field_health_score': self._calculate_field_health_score(field)
            }
            
            return metrics    

        except Field.DoesNotExist: 
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
    


class Field(models.Model):
    SOIL_TYPES = [
        ('sandy', 'Qumlu'),
        ('clay', 'Gil'),
        ('loamy', 'Humuslu'),
        ('silty', 'Limli'),
        ('peat', 'Torf'),
    ]


    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    area_hectares = models.DecimalField(max_digits=10,decimal_places=2)
    soil_type = models.CharField(max_length=20, choices=SOIL_TYPES, default='loamy')
    created_at = models.DateTimeField(auto_now_add=True)
    objects = FieldManager()

    def __str__(self):
        return f'{self.name} - {self.area_hectares} ha'

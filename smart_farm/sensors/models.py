from django.db import models
from django.conf import settings    
from fields.models import Field
 




class SensorManager(models.Manager):

    def search_sensor(self, query, user, filters=None):

        qs = self.filter(user=user)
        
        if query:
            qs = qs.filter(
                models.Q(field__name__icontains = query) |
                models.Q(sensor_code__icontains = query) |
                models.Q(name__icontains = query) |
                models.Q(sensor_type = query)
            )

        if filters:
            sensor_type = filters.get('sensor_type')
            is_active = filters.get('is_active')
            battery_level = filters.get('battery_level')
            
            if sensor_type:
                qs = qs.filter(sensor_type=sensor_type)
            if is_active:
                
                is_active_bool = is_active.lower() == 'true'
                qs = qs.filter(is_active=is_active_bool)
            if battery_level:
               
                if battery_level == 'high':
                    qs = qs.filter(battery_level__gt=70)
                elif battery_level == 'medium':
                    qs = qs.filter(battery_level__range=(30, 70))
                elif battery_level == 'low':
                    qs = qs.filter(battery_level__lt=30)     

        return qs.select_related('field')           


    def get_real_time_data(self, sensor_ids):
        
        from django.utils import timezone
        from datetime import timedelta
        
        sensors = self.filter(id__in=sensor_ids)
        real_time_data = {}
        
        for sensor in sensors:
            
            one_hour_ago = timezone.now() - timedelta(hours=1)
            
            recent_readings = sensor.readings.filter(
                recorded_at__gte=one_hour_ago
            ).order_by('-recorded_at')
            
            if recent_readings.exists():
                latest_reading = recent_readings.first()
                
                sensor_data = {
                    'sensor_name': sensor.name,
                    'sensor_type': sensor.get_sensor_type_display(),
                    'latest_value': float(latest_reading.value),
                    'unit': latest_reading.unit,
                    'recorded_at': latest_reading.recorded_at,
                    'battery_level': float(sensor.battery_level),
                    'battery_status': sensor.battery_status(),
                    'is_active': sensor.is_active,
                    'data_quality': 'good',  
                    'trend': self._calculate_trend(recent_readings),
                    'alerts': self._check_alerts(sensor, latest_reading)
                }
                
                real_time_data[sensor.id] = sensor_data
            else:
                real_time_data[sensor.id] = {
                    'sensor_name': sensor.name,
                    'error': 'Son 1 saatlıq məlumat yoxdur',
                    'battery_level': float(sensor.battery_level),
                    'is_active': sensor.is_active
                }
        
        return real_time_data
    
    def _calculate_trend(self, readings):
        
        if len(readings) < 2:
            return 'stable'
        
        values = [float(reading.value) for reading in readings[:10]]  
        if len(values) < 2:
            return 'stable'
        
       
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        difference = second_half - first_half
        percentage_change = (difference / first_half) * 100 if first_half != 0 else 0
        
        if percentage_change > 5:
            return 'increasing'
        elif percentage_change < -5:
            return 'decreasing'
        else:
            return 'stable'
    
    def _check_alerts(self, sensor, latest_reading):
        
        alerts = []
        
        
        if sensor.battery_level < 20:
            alerts.append({
                'type': 'warning',
                'message': 'Batareya səviyyəsi aşağıdır',
                'priority': 'high' if sensor.battery_level < 10 else 'medium'
            })
        
        
        if not sensor.is_active:
            alerts.append({
                'type': 'error',
                'message': 'Sensor aktiv deyil',
                'priority': 'high'
            })
        
       
        threshold_alerts = self._check_thresholds(sensor, latest_reading)
        alerts.extend(threshold_alerts)
        
        return alerts
    
    def _check_thresholds(self, sensor, reading):
        """Sensor tipinə görə həddi dəyərləri yoxlayır"""
        thresholds = {
            'soil_moisture': {'min': 20, 'max': 80},
            'temperature': {'min': 5, 'max': 35},
            'humidity': {'min': 30, 'max': 80},
            'ph': {'min': 5.5, 'max': 7.5},
        }
        
        alerts = []
        sensor_type = sensor.sensor_type
        value = float(reading.value)
        
        if sensor_type in thresholds:
            limits = thresholds[sensor_type]
            
            if value < limits['min']:
                alerts.append({
                    'type': 'warning',
                    'message': f'{sensor_type} həddindən aşağı: {value}',
                    'priority': 'medium'
                })
            elif value > limits['max']:
                alerts.append({
                    'type': 'warning', 
                    'message': f'{sensor_type} həddindən yuxarı: {value}',
                    'priority': 'medium'
                })
        
        return alerts


class Sensor(models.Model):
     
    SENSOR_TYPES = [
        ('soil_moisture', '🌱 Torpaq Nəmliyi'),
        ('temperature', '🌡️ Temperatur'),
        ('humidity', '💧 Rütubət'),
        ('ph', '⚗️ pH Səviyyəsi'),
        ('nutrient', '🧪 Qida Maddələri'),
        ('light', '☀️ İşıq Intensivliyi'),
        ('rainfall', '🌧️ Yağış'),
    ]
    
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='sensors') 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Sensor adı')
    sensor_code = models.CharField(max_length=50, unique=True, verbose_name='Sensor kodu')  
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPES, verbose_name='Sensor növü')
    description = models.TextField(blank=True, verbose_name='Təsvir')
    installation_date = models.DateField(verbose_name='Qurulma tarixi')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Enlik')  
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Uzunluq')
    battery_level = models.DecimalField(max_digits=5, decimal_places=2, default=100, verbose_name='Batareya səviyyəsi (%)')
    data_interval = models.IntegerField(default=60, verbose_name='Məlumat intervalı (dəq)')
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    last_maintenance = models.DateField(null=True, blank=True, verbose_name='Son texniki qulluq')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = SensorManager()

    def __str__(self):
        return f"{self.name} ({self.get_sensor_type_display()})"  
    
    def battery_status(self):
        if self.battery_level > 70:
            return 'success'
        elif self.battery_level > 30:
            return 'warning'
        else:
            return 'danger'
            
    class Meta:
        ordering = ['-installation_date'] 
        verbose_name = 'Sensor'  
        verbose_name_plural = 'Sensorlar'   


class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='readings')
    value = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='Dəyər')
    unit = models.CharField(max_length=20, verbose_name='Vahid')
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name='Qeyd tarixi')
    
    def __str__(self):
        return f"{self.sensor.name} - {self.value} {self.unit}"
    
    class Meta:
        ordering = ['-recorded_at']  
        verbose_name = 'Sensor məlumatı'
        verbose_name_plural = 'Sensor məlumatları'        


 
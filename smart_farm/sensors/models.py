from django.db import models
from django.conf import settings    
from fields.models import Field
 
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


 
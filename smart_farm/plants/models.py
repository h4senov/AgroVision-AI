from django.db import models
from django.conf import settings
from fields.models import Field


class PlantManager(models.Manager):

    def search_plants(self, query, user, filters=None):
        
        qs  = self.filter(user=user)

        if query:
            qs = qs.filter(
                models.Q(variety__icontains = query) |
                models.Q(plant_type  = query) |
                models.Q(field__name__icontains = query)
            )

        if filters:
            plant_type = filters.get('plant_type')
            growth_stage = filters.get('growth_stage')
            status = filters.get('status')
            
            if plant_type:
                qs = qs.filter(plant_type=plant_type)
            if growth_stage:
                qs = qs.filter(growth_stage=growth_stage)
            if status:
                qs = qs.filter(status=status)              

        return qs.select_related('field')         

    def predict_harvest_time(self, plant_id):
       
        try:
            plant = self.get(id=plant_id)
            
            
            growth_periods = {
                'wheat': 120,      
                'corn': 90,        
                'barley': 110,     
                'sunflower': 85,  
                'cotton': 160,     
                'tomato': 75,      
                'potato': 100,
                'other': 90,      
            }
            
            base_growth_days = growth_periods.get(plant.plant_type, 90)
            
            
            weather_factor = self._calculate_weather_factor(plant.field)
            
           
            health_factor = self._calculate_health_factor(plant)
            
           
            adjusted_growth_days = base_growth_days * weather_factor * health_factor
            
            
            from django.utils import timezone
            predicted_harvest_date = plant.planting_date + timezone.timedelta(days=adjusted_growth_days)
            
            prediction = {
                'plant_name': str(plant),
                'planting_date': plant.planting_date,
                'base_growth_days': base_growth_days,
                'adjusted_growth_days': round(adjusted_growth_days),
                'predicted_harvest_date': predicted_harvest_date,
                'days_remaining': (predicted_harvest_date - timezone.now().date()).days,
                'confidence_score': round(min(weather_factor * health_factor * 100, 95), 2),
                'factors': {
                    'weather_impact': round((weather_factor - 1) * 100, 2),
                    'health_impact': round((health_factor - 1) * 100, 2),
                }
            }
            
            return prediction
            
        except Plant.DoesNotExist:
            return {'error': 'Bitki tapılmadı'}
    
    def _calculate_weather_factor(self, field):
        """Hava şəraitinin təsirini hesablayır"""
       
        from django.utils import timezone
        from datetime import timedelta
        month_ago = timezone.now().date() - timedelta(days=30)
        
        weather_data = field.weather_data.filter(weather_date__gte=month_ago)
        
        if not weather_data.exists():
            return 1.0  
        
        avg_temp = weather_data.aggregate(avg=models.Avg('temperature_avg'))['avg']
        total_rain = weather_data.aggregate(total=models.Sum('precipitation_mm'))['total']
        
       
        temp_factor = 1.0
        if avg_temp < 10:
            temp_factor = 0.8  
        elif avg_temp > 30:
            temp_factor = 0.9  
        elif 15 <= avg_temp <= 25:
            temp_factor = 1.1 
        
        rain_factor = 1.0
        if total_rain < 20:
            rain_factor = 0.8 
        elif total_rain > 100:
            rain_factor = 0.9 
        elif 40 <= total_rain <= 80:
            rain_factor = 1.1 
        
        return (temp_factor + rain_factor) / 2
    
    def _calculate_health_factor(self, plant):
       
        growth_factors = {
            'seedling': 0.8,
            'vegetative': 1.0,
            'flowering': 1.1,
            'fruiting': 1.2,
            'mature': 1.0,
            'harvested': 0.0,
        }
        
        growth_factor = growth_factors.get(plant.growth_stage, 1.0)
        
        
        status_factor = 1.0
        if plant.status == 'diseased':
            status_factor = 0.7
        elif plant.status == 'failed':
            status_factor = 0.5
        
        return growth_factor * status_factor





class Plant(models.Model):
    PLANT_TYPES = [
        ('wheat', 'Buğda'),
        ('corn', 'Qarğıdalı'),
        ('barley', 'Arpa'),
        ('sunflower', 'Günəbaxan'),
        ('cotton', 'Pambıq'),
        ('tomato', 'Pomidor'),
        ('potato', 'Kartof'),
        ('other', 'Digər'),
    ]
    
    GROWTH_STAGES = [
        ('seedling', 'Cücərti'),
        ('vegetative', 'Vegetativ'),
        ('flowering', 'Çiçəkləmə'),
        ('fruiting', 'Meyvə'),
        ('mature', 'Yetişmiş'),
        ('harvested', 'Yığılmış'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Aktiv'),
        ('harvested', 'Yığılıb'),
        ('failed', 'Uğursuz'),
        ('diseased', 'Xəstə'),
    ]
    
    field = models.ForeignKey(
        Field, 
        on_delete=models.CASCADE, 
        related_name='plants',
        verbose_name='Sahə'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name='İstifadəçi'
    )
    plant_type = models.CharField(
        max_length=20, 
        choices=PLANT_TYPES,
        verbose_name='Bitki növü'
    )
    variety = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Sort'
    )
    planting_date = models.DateField(
        verbose_name='Əkmə tarixi'
    )
    expected_harvest_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Gözlənilən yığım tarixi'
    )
    actual_harvest_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Həqiqi yığım tarixi'
    )
    growth_stage = models.CharField(
        max_length=20, 
        choices=GROWTH_STAGES, 
        default='seedling',
        verbose_name='Böyümə mərhələsi'
    )
    area_hectares = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        verbose_name='Sahə (hektar)'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name='Status'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Qeydlər'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaradılma tarixi'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Yenilənmə tarixi'
    )

    objects = PlantManager()
    
    def __str__(self):
        return f"{self.get_plant_type_display()} - {self.field.name}"
    
    def days_since_planting(self):
        from django.utils import timezone
        return (timezone.now().date() - self.planting_date).days
    
    def is_harvest_due(self):
        if self.expected_harvest_date and self.status == 'active':
            from django.utils import timezone
            return timezone.now().date() >= self.expected_harvest_date
        return False
    
    class Meta:
        ordering = ['-planting_date']
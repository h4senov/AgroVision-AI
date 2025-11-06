from django.db import models
from django.conf import settings
from fields.models import Field

# plants/models.py - Plant modelinə əlavə edirəm
class PlantManager(models.Manager):
    def predict_harvest_time(self, plant_id):
        """
        Bitkinin yığım vaxtını proqnozlaşdırır
        """
        try:
            plant = self.get(id=plant_id)
            
            # Bitki növünə görə orta yetişmə müddəti (günlər)
            growth_periods = {
                'wheat': 120,      # Buğda
                'corn': 90,        # Qarğıdalı
                'barley': 110,     # Arpa
                'sunflower': 85,   # Günəbaxan
                'cotton': 160,     # Pambıq
                'tomato': 75,      # Pomidor
                'potato': 100,     # Kartof
                'other': 90,       # Digər
            }
            
            base_growth_days = growth_periods.get(plant.plant_type, 90)
            
            # İklim şəraitinə görə tənzimləmə
            weather_factor = self._calculate_weather_factor(plant.field)
            
            # Bitki sağlamlığına görə tənzimləmə
            health_factor = self._calculate_health_factor(plant)
            
            # Ümumi yetişmə müddəti
            adjusted_growth_days = base_growth_days * weather_factor * health_factor
            
            # Proqnozlaşdırılan yığım tarixi
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
        # Son 30 günlük hava məlumatları
        from django.utils import timezone
        from datetime import timedelta
        month_ago = timezone.now().date() - timedelta(days=30)
        
        weather_data = field.weather_data.filter(weather_date__gte=month_ago)
        
        if not weather_data.exists():
            return 1.0  # Default faktor
        
        avg_temp = weather_data.aggregate(avg=models.Avg('temperature_avg'))['avg']
        total_rain = weather_data.aggregate(total=models.Sum('precipitation_mm'))['total']
        
        # Optimal temperatur və yağıntıya görə tənzimləmə
        temp_factor = 1.0
        if avg_temp < 10:
            temp_factor = 0.8  # Çox soyuq
        elif avg_temp > 30:
            temp_factor = 0.9  # Çox isti
        elif 15 <= avg_temp <= 25:
            temp_factor = 1.1  # Optimal
        
        rain_factor = 1.0
        if total_rain < 20:
            rain_factor = 0.8  # Quraq
        elif total_rain > 100:
            rain_factor = 0.9  # Çox yağışlı
        elif 40 <= total_rain <= 80:
            rain_factor = 1.1  # Optimal
        
        return (temp_factor + rain_factor) / 2
    
    def _calculate_health_factor(self, plant):
        """Bitki sağlamlığının təsirini hesablayır"""
        # Böyümə mərhələsinə görə
        growth_factors = {
            'seedling': 0.8,
            'vegetative': 1.0,
            'flowering': 1.1,
            'fruiting': 1.2,
            'mature': 1.0,
            'harvested': 0.0,
        }
        
        growth_factor = growth_factors.get(plant.growth_stage, 1.0)
        
        # Statusa görə
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
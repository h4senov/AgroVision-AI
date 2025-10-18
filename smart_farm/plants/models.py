from django.db import models
from django.conf import settings
from fields.models import Field

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
    
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='plants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plant_type = models.CharField(max_length=20, choices=PLANT_TYPES)
    variety = models.CharField(max_length=100, blank=True)
    planting_date = models.DateField()
    expected_harvest_date = models.DateField(null=True, blank=True)
    actual_harvest_date = models.DateField(null=True, blank=True)
    growth_stage = models.CharField(max_length=20, choices=GROWTH_STAGES, default='seedling')
    area_hectares = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
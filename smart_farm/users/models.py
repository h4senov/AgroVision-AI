from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser): 
    ROLE_CHOICES = [
        ('farmer', '👨‍🌾 Fermer'),
        ('expert', '👨‍🔬 Mütəxəssis'),
        ('guest', '👋 Qonaq'),
        ('admin', '👨‍💼 Admin'),
    ]

    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    farm_name = models.CharField(max_length=100, blank=True, verbose_name='Ferma adı')
    location = models.CharField(max_length=255, blank=True, verbose_name='Yerləşdiyi yerin')    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='guest',
        verbose_name='Rol'
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='Son giriş')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaradılma tarixi')
    
    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'
    
    def get_fields_count(self):
        from fields.models import Field 
        return Field.objects.filter(user=self).count()
    
    def get_plants_count(self):
        from plants.models import Plant
        return Plant.objects.filter(field__user=self).count()
    
    def get_sensors_count(self):
        from sensors.models import Sensor
        return Sensor.objects.filter(field__user=self).count()
    
    def get_inventory_count(self):
        from inventory.models import Inventory
        return Inventory.objects.filter(user=self).count()

    def get_activity_level(self):
        total_entities = (
            self.get_fields_count() + 
            self.get_plants_count() + 
            self.get_sensors_count() + 
            self.get_inventory_count()
        )
        
        if total_entities > 20:
            return 'high'
        elif total_entities > 10:
            return 'medium'
        else:
            return 'low'

    def get_last_activity_days(self):   
        if self.last_login:
            return (timezone.now() - self.last_login).days
        return None
    
    def can_deactivate_users(self):
        
        return self.role == 'admin' or self.is_superuser
    
    class Meta:
        verbose_name = 'İstifadəçi'
        verbose_name_plural = 'İstifadəçilər'
        ordering = ['-date_joined']
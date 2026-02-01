from django.db import models
from django.contrib.auth.models import AbstractUser
from django.apps import apps 
from django.utils import timezone

class CustomUser(AbstractUser): 
    ROLE_CHOICES = [
        ('farmer', '👨‍🌾 Fermer'),
        ('expert', '👨‍🔬 Mütəxəssis'),
        ('guest', '👋 Qonaq'),
        ('admin', '👨‍💼 Admin'),
    ]

    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    farm_name = models.CharField(max_length=100, blank=True, verbose_name='Ferma adı')
    location = models.CharField(max_length=255, blank=True, verbose_name='Yerləşdiyi yer')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Profil şəkli')
    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='guest',
        verbose_name='Rol'
    )

    # Dinamik model çağırma helperi
    def _get_count(self, model_name, app_label):
        try:
            Model = apps.get_model(app_label=app_label, model_name=model_name)
            if model_name == 'Inventory':
                return Model.objects.filter(user=self).count()
            elif model_name == 'Field':
                return Model.objects.filter(user=self).count()
            else: # Plant və Sensor üçün (field üzərindən)
                return Model.objects.filter(field__user=self).count()
        except (LookupError, Exception):
            return 0

    def get_fields_count(self):
        return self._get_count('Field', 'fields')
    
    def get_plants_count(self):
        return self._get_count('Plant', 'plants')
    
    def get_sensors_count(self):
        return self._get_count('Sensor', 'sensors')
    
    def get_inventory_count(self):
        return self._get_count('Inventory', 'inventory')

    def get_last_activity_days(self):   
        if self.last_login:
            return (timezone.now() - self.last_login).days
        return None

    def get_activity_level(self):
        total = self.get_fields_count() + self.get_plants_count() + self.get_sensors_count()
        if total > 20: return 'high'
        if total > 5: return 'medium'
        return 'low'

    def can_manage_system(self):
        return self.role == 'admin' or self.is_superuser

    class Meta:
        verbose_name = 'İstifadəçi'
        verbose_name_plural = 'İstifadəçilər'
        ordering = ['-date_joined']
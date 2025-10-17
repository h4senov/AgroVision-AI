from django.db import models
from users.models import CustomUser
# Create your models here.

class Field(models.Model):
    SOIL_TYPES = [

        ('sandy','Sandy'),
        ('clay','Clay'),
        ('loamy','Loamy'),
        ('silty','Silty'),
        ('peat','Peat'),

    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    area_hectares = models.DecimalField(max_digits=10,decimal_places=2)
    soil_type = models.CharField(max_length=20, choices=SOIL_TYPES, default='loamy')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.area_hectares} ha'
    
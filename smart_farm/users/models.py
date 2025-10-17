from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class CustomUser(AbstractUser): 

    phone = models.CharField(max_length=20, blank=True)
    farm_name = models.CharField(max_length=100,blank=True)
    location = models.CharField(max_length=255,blank=True)

    def __str__(self):
        return self.username
    
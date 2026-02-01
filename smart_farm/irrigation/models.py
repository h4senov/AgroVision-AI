from django.db import models
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta

class IrrigationManager(models.Manager):
    def search_irrigation(self, query, user=None, filters=None):
        qs = self.get_queryset()
        
        if user:
            qs = qs.filter(field__user=user)
        
        if query:
            qs = qs.filter(
                Q(field__name__icontains=query) |
                Q(plant__name__icontains=query) |
                Q(notes__icontains=query) |
                Q(applied_fertilizer__icontains=query)
            )
        
        if filters:
            irrigation_type = filters.get('irrigation_type')
            status = filters.get('status')
            start_date = filters.get('start_date')
            end_date = filters.get('end_date')
            field_id = filters.get('field')

            if irrigation_type:
                qs = qs.filter(irrigation_type=irrigation_type)
            if status:
                qs = qs.filter(status=status)
            if field_id:
                qs = qs.filter(field_id=field_id)
            if start_date:
                qs = qs.filter(irrigation_date__gte=start_date)
            if end_date:
                qs = qs.filter(irrigation_date__lte=end_date)
                
        return qs


class IrrigationSchedule(models.Model):
    IRRIGATION_TYPE = [ 
    ('drip', '💧 Damcıla suvarma'),        
    ('sprinkler', '🚿 Yağışyağdırma'),     
    ('pivot', '🎡 Pivot (Dairəvi)'),       
    ('flood', '🌊 Sel (Arx) suvarma'),       
    ('subsurface', '🚜 Torpaqaltı'),      
]    

    STATUS_CHOICES = [
        ('planned', 'Planlaşdırılıb'), 
        ('active', 'Davam edir'), 
        ('completed', 'Tamamlandı'), 
        ('failed', 'Xəta')
    ]

    field = models.ForeignKey(
        'fields.Field',
        on_delete=models.CASCADE,
        related_name='field_irrigation_records',
        verbose_name='Sahə'
    )
    plant = models.ForeignKey(
        'plants.Plant',
        on_delete=models.CASCADE,
        related_name='plant_irrigation_records',
        null=True,
        blank=True,
        verbose_name='Bitki'
    )
    irrigation_date = models.DateField(default=timezone.now, verbose_name='Sulama tarixi')
    irrigation_type = models.CharField(max_length=20, choices=IRRIGATION_TYPE, verbose_name='Sulama növü')
    water_volume_liters = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Su həcmi (litrlər)')
    notes = models.TextField(blank=True, verbose_name='Qeydlər')
    
    is_automated = models.BooleanField(default=False, verbose_name='Avtomatlaşdırılmış')
    start_time = models.TimeField(null=True, blank=True, verbose_name='Başlama vaxtı')
    end_time = models.TimeField(null=True, blank=True, verbose_name='Bitmə vaxtı')
    
    soil_moisture_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Torpaq rütubəti (%)")
    applied_fertilizer = models.CharField(max_length=100, blank=True, verbose_name="Verilən gübrə")
    energy_consumption = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Enerji sərfi (kWh)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed', verbose_name='Status')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaradılma tarixi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yenilənmə tarixi')

    objects = IrrigationManager()

    class Meta:
        ordering = ['-irrigation_date', '-start_time']
        verbose_name = 'Suvarma'
        verbose_name_plural = 'Suvarmalar'

    def __str__(self):
        plant_name = self.plant.name if self.plant else "Ümumi"
        return f"{self.irrigation_date} | {self.field.name} - {self.get_irrigation_type_display()}"

    def duration_minutes(self):
        if self.start_time and self.end_time:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            
            diff = end_minutes - start_minutes
            if diff < 0:
                diff += 24 * 60
            return diff
        return 0

    def calculate_cost(self, water_price=0, energy_price=0):
        total = Decimal('0.00')
        if self.water_volume_liters and water_price:
            total += self.water_volume_liters * Decimal(str(water_price))
        if self.energy_consumption and energy_price:
            total += self.energy_consumption * Decimal(str(energy_price))
        return total
    
    @classmethod
    def total_consumption_today(cls, user):
        """Bu gün istifadə olunan ümumi su həcmi."""
        today = timezone.now().date()
        return cls.objects.filter(
            field__user=user, 
            irrigation_date=today, 
            status='completed'
        ).aggregate(models.Sum('water_volume_liters'))['water_volume_liters__sum'] or 0

    @classmethod
    def next_upcoming_irrigation(cls, user):
        """Ən yaxın vaxtda planlaşdırılan suvarmanı tapır."""
        now = timezone.now()
        return cls.objects.filter(
            field__user=user,
            status='planned',
            irrigation_date__gte=now.date()
        ).order_by('irrigation_date', 'start_time').first()

    def time_until(self):
        """Suvarmaya qalan vaxtı formatlanmış şəkildə qaytarır (məs: 2s 15d)."""
        if not self.start_time:
            return "Vaxt təyin edilməyib"
        
        now = timezone.now()
        start_datetime = timezone.make_aware(datetime.combine(self.irrigation_date, self.start_time))
        diff = start_datetime - now
        
        if diff.total_seconds() < 0:
            return "Vaxt keçib"
            
        hours = int(diff.total_seconds() // 3600)
        minutes = int((diff.total_seconds() % 3600) // 60)
        return f"{hours}s {minutes}d"
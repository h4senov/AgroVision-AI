from decimal import Decimal
import os
from django.db import models
from django.conf import settings


class InventoryManager(models.Manager):
    def search_inventory(self, query, user, filters=None):
        qs = self.filter(user=user)
        
        if query:
            qs = qs.filter(
                models.Q(item_name__icontains=query) |
                models.Q(item_code__icontains=query) |
                models.Q(supplier_name__icontains=query)
            )
        
        if filters:
            category = filters.get('category')
            min_stock = filters.get('min_stock')
            max_stock = filters.get('max_stock')
            
            if category:
                qs = qs.filter(category=category)
            if min_stock:
                qs = qs.filter(quantity__gte=min_stock)
            if max_stock:
                qs = qs.filter(quantity__lte=max_stock)
                
        return qs

def inventory_image_path(instance, filename):

    name, ext = os.path.splitext(filename)
    clean_name = name.replace(" ", "_")

    return f"inventory/user_{instance.user.id}/{instance.category}/{clean_name}{ext}"

class Inventory(models.Model):
    CATEGORY_CHOICES = [
        ('seeds', '🌱 Toxumlar'),
        ('fertilizers', '🧪 Gübrələr'),
        ('pesticides', '🐛 Zəhərlər'),
        ('herbicides', '🌿 Herbisidlar'),
        ('equipment', '🔧 Avadanlıq'),
        ('tools', '🛠️ Alətlər'),
        ('spare_parts', '⚙️ Ehtiyat Hissələr'),
        ('fuel', '⛽ Yanacaq'),
    ]
    
    UNIT_CHOICES = [
        ('kg', 'Kiloqram (kg)'),
        ('g', 'Qram (g)'),
        ('l', 'Litr (l)'),
        ('ml', 'Millilitr (ml)'),
        ('pcs', 'Ədəd (pcs)'),
        ('boxes', 'Qutu (boxes)'),
        ('tons', 'Ton (tons)'),
    ]

    STORAGE_CHOICES = [
        ('main_warehouse', 'Əsas Anbar'),
        ('cold_storage', 'Soyuducu Anbar'),
        ('shelf_a', 'Rəf A'),
        ('shelf_b', 'Rəf B'),
        ('external', 'Xarici Sahə'),
        ('other', 'Digər'),
    ]



    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100, verbose_name='Məhsul adı')
    item_code = models.CharField(max_length=50, unique=True, verbose_name='Məhsul kodu')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Kateqoriya')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Miqdar')
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, verbose_name='Vahid')
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Minimum stok')
    max_stock_level = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Maksimum stok')
    supplier_name = models.CharField(max_length=100, blank=True, verbose_name='Təchizatçı')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Vahid qiyməti')
    total_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='Ümumi dəyər')
    expiration_date = models.DateField(null=True, blank=True, verbose_name='Son istifadə tarixi')
    storage_location = models.CharField(
        max_length=50, 
        blank=True,
        choices=STORAGE_CHOICES, 
        default='main_warehouse',
        verbose_name='Saxlama yeri'
    )
    notes = models.TextField(blank=True, verbose_name='Qeydlər')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(
        upload_to=inventory_image_path,  
        null=True,
        blank=True,
        verbose_name='Şəkil',
        help_text='Məhsulun şəklini yükləyin (max 5MB)',
        validators=[]   
    )
    def __str__(self):
        return f"{self.item_name} ({self.quantity} {self.unit})"
    
    @property
    def stock_status(self):
        if self.min_stock_level and self.quantity <= self.min_stock_level:
            return 'low'
        elif self.max_stock_level and self.quantity >= self.max_stock_level:
            return 'high'
        else:
            return 'normal'

    def days_until_expiration(self):
        if self.expiration_date:
            from django.utils import timezone
            today = timezone.now().date()
            return (self.expiration_date - today).days
        return None

    def is_expired(self):
        days = self.days_until_expiration()
        return days is not None and days < 0

    def calculate_total_value(self):
        if self.quantity and self.unit_price:
            return self.quantity * self.unit_price
        return Decimal('0.00')
    
    def save(self, *args, **kwargs):  
        if self.quantity and self.unit_price:
            self.total_value = self.calculate_total_value()
        super().save(*args, **kwargs)

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default_inventory.png'
    
    def image_preview(self):
        if self.image:
            from django.utils.html import format_html
            return format_html(
                '<img src="{}" width="500" height="500" style="object-fit: cover; border-radius: 4px;" />',
                self.image.url
            )
        return "-"
    image_preview.short_description = 'Şəkil önizləməsi'


    class Meta:
        verbose_name = 'Anbar məhsulu'
        verbose_name_plural = 'Anbar məhsulları'
        ordering = ['-created_at']
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils import timezone



class ProductManager(models.Manager):

    def search_products(self, query=None, filters=None):
        # default queryset
        qs = self.filter(
            is_published=True,
            deleted_at__isnull=True
        ).select_related('category').prefetch_related('tags')

        # --- SEARCH ---
        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(short_description__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()

        # --- FILTERS ---
        if filters:
            category = filters.get("category")
            tag = filters.get("tag")
            is_featured = filters.get("is_featured")
            min_price = filters.get("min_price")
            max_price = filters.get("max_price")
            in_stock = filters.get("in_stock")

            if category:
                qs = qs.filter(category__slug=category)

            if tag:
                qs = qs.filter(tags__name__iexact=tag)

            if is_featured:
                qs = qs.filter(is_featured=True)

            if min_price:
                qs = qs.filter(price__gte=min_price)

            if max_price:
                qs = qs.filter(price__lte=max_price)

            if in_stock:
                qs = qs.filter(stock__gt=0)

        return qs


# Kateqoriya
class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    def __str__(self):
        return self.name

# Tag (sadə)
class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name

# Əsas Product modeli
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    short_description = models.CharField(max_length=400, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_published = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Soft delete
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    objects = ProductManager()

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    @property
    def is_deleted(self):
        return self.deleted_at is not None

# Çoxlu product şəkilləri
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/images/')
    alt = models.CharField(max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

# İstifadəçi reytinqləri (optional user requirement)
class ProductRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    score = models.PositiveSmallIntegerField()  # 1..5
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.product.name} — {self.score}"

# Simple statistics snapshot (optional)
class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

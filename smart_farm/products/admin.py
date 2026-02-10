from django.contrib import admin
from .models import Category, Tag, Product, ProductImage, ProductRating, ProductView

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Varsayılan olaraq 1 boş şəkil yeri göstər

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_published', 'is_featured', 'created_at')
    list_filter = ('is_published', 'is_featured', 'category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]  # Şəkilləri birbaşa məhsul səhifəsində əlavə etmək üçün
    list_editable = ('price', 'stock', 'is_published') # Siyahıdan sürətli redaktə

# Opsional: Reytinq və Baxışları görmək üçün
admin.site.register(ProductRating)
admin.site.register(ProductView)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Product, Category, ProductImage, ProductView, Tag
from .forms import ProductForm # Bu formu yaratmalısan (ModelForm)

# --- İSTİFADƏÇİ (QONAQ) ÜÇÜN VİEWLAR ---

def product_list(request):
    query = request.GET.get("q")

    filters = {
        "category": request.GET.get("category"),
        "tag": request.GET.get("tag"),
        "is_featured": request.GET.get("featured"),
        "min_price": request.GET.get("min_price"),
        "max_price": request.GET.get("max_price"),
        "in_stock": request.GET.get("in_stock"),
    }

    products = Product.objects.search_products(
        query=query,
        filters=filters
    )

    categories = Category.objects.all()

    return render(request, "products/product_list.html", {
        "products": products,
        "categories": categories
    })

def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images', 'tags'),
        pk=pk,
        deleted_at__isnull=True
    )

    # IP qeydiyyatı
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    ProductView.objects.create(product=product, ip=ip)

    related_products = Product.objects.filter(
        category=product.category,
        is_published=True,
        deleted_at__isnull=True
    ).exclude(pk=pk)[:4]

    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products
    })


# --- ADMİN / İŞÇİ ÜÇÜN VİEWLAR (CRUD) ---

# Yalnız superuser və ya müəyyən səlahiyyəti olanlar girə bilsin
def is_staff_check(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff_check)
def product_create(request):
    """Yeni məhsul əlavə etmək"""
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Yeni Məhsul'})

@login_required
@user_passes_test(is_staff_check)
def product_update(request, pk):
    """Məhsulu redaktə etmək"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Məhsulu Redaktə Et'})

@login_required
@user_passes_test(is_staff_check)
def product_delete(request, pk):
    """Məhsulu silmək (Soft Delete məntiqi ilə)"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.soft_delete() # Modelində yazdığımız soft_delete funksiyası
        return redirect('products:product_list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})
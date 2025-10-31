from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from .models import Inventory
from .forms import Inventory, InventoryFilterForm, InventoryForm, InventorySearchForm
from django.db.models import Sum 
from decimal import Decimal



@login_required
def inventory_list(request):
    items = Inventory.objects.filter(user=request.user)
    
    search_query = request.GET.get('search','')
    category_filter = request.GET.get('category','')
    stock_status_filter = request.GET.get('stock_status','')

    if search_query:
        items = items.filter(
            Q(items_name__icontains=search_query) |
            Q(item_code__icontains=search_query) |
            Q(supplier_name__icontains=search_query)
        )

    if category_filter:
        items =  items.filter(category=category_filter)


    if stock_status_filter:
        if stock_status_filter == 'low':
            items = [item for item in items if item.stock_status() == 'low']
        elif stock_status_filter == 'normal':
            items = [item for item in items if item.stock_status() == 'normal']
        elif stock_status_filter == 'high':
            items = [item for item in items if item.stock_status() == 'high']       


    search_form = InventorySearchForm(initial={'search': search_query})
    filter_form = InventoryFilterForm(initial={
        'category': category_filter,
        'stock_status': stock_status_filter
    })
    
    context = {
        'items': items,
        'search_form': search_form,
        'filter_form': filter_form,
    }
    
    return render(request, 'inventory/inventory_list.html', context)

@login_required
def inventory_detail(request, item_id):
    item = get_object_or_404(Inventory,id=item_id, user = request.user)
    return render(request, 'inventory/inventory_detail.html', {'item' : item})

@login_required
def add_inventory(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()

            messages.success(request, 'Məhsul uğurla əlavə edildi!')
            return redirect('inventory:inventory_list')
    else:
        form =InventoryForm()


    return render(request, 'inventory/add_inventory.html', {'form': form})

@login_required
def edit_inventory(request, item_id):
    item = get_object_or_404(Inventory, id=item_id, user=request.user)
    if request.method == 'POST':
        form = InventoryForm(request.POST,instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Məhsul məlumatları uğurla yeniləndi!')
            return redirect('inventory:inventory_detail', item_id=item.id)
    else:
        form = InventoryForm(instance=item)
    
    return render(request, 'inventory/edit_inventory.html', {'form': form, 'item': item})

@login_required
def delete_inventory(request, item_id):

    item = get_object_or_404(Inventory, id=item_id, user=request.user)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, '🗑️ Məhsul uğurla silindi!')
        return redirect('inventory_list')
    
    return render(request, 'inventory/delete_inventory.html', {'item': item})

@login_required
def get_inventory_status(request):

    user_inventory = Inventory.objects.filter(user=request.user)

    total_items = user_inventory.count()
    total_value =  user_inventory.aggregate(total=Sum('total_value'))['total'] or 0 

    low_stock_count = user_inventory.filter(
        min_stock_level__isnull = False,
        quantity__lte=F('min_stock_level')
    ).count()

    context = {
        'total_items': total_items,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'inventory_items': user_inventory,
    }

    return render(request, 'inventory/status.html', context)

@login_required
def track_inventory_usage(request,item_id):

    item =  get_object_or_404(Inventory, id=item_id, user = request.user)

    if request.method == 'POST':
        used_quantity = request.POST.get('used_quantity')

        try:
            used_quantity = Decimal(used_quantity)
            if used_quantity > 0 and used_quantity <= item.quantity:
                item.quantity -= used_quantity
                item.save()
                messages.success(request, f'{used_quantity} {item.unit} istifadə edildi')
                return redirect('inventory:inventory_detail', item_id=item.id)
            else:
                messages.error(request, 'Keçərsiz miqdar!')
        except (ValueError, TypeError):
            messages.error(request, 'Xətalı miqdar!')
    
    return render(request, 'inventory/track_usage.html', {'item': item})

@login_required
def check_low_stock(request):
    user_inventory = Inventory.objects.filter(user=request.user)
    

    low_stock_items = [
        item for item in user_inventory 
        if item.stock_status() == 'low'
    ]
    

    context = {
        'low_stock_items': low_stock_items,
        'low_stock_count': len(low_stock_items),
    }
    
    return render(request, 'inventory/low_stock.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.db.models import Sum 
from decimal import Decimal
# ------------------------------------------------/
from django.views.generic import ListView, DetailView, UpdateView, DeleteView,CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Inventory
from .forms import InventoryForm, InventorySearchForm, InventoryFilterForm

class InventoryListView(LoginRequiredMixin, ListView):
    model = Inventory
    template_name = 'inventiry/inventory_list.html'
    context_object_name = 'items' 
    paginate_by = 10

    def get_queryset(self):

        inventory = super().get_queryset().filter(user=self.request.user)
        
        search_query = self.request.GET.get('search','')
        if search_query:
            inventory = inventory.filter(
                Q(item_name__icontains=search_query) |
                Q(item_code__icontains=search_query) |
                Q(supplier_name__icontains=search_query)
            )
        
        category_filter = self.request.GET.get('category','')

        if category_filter:
            inventory = inventory.filter(category=category_filter)

        return inventory
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get('search', '')
        category_filter = self.request.GET.get('category', '')

        context['search_form'] = InventorySearchForm(initial={'search': search_query})
        context['filter_form'] = InventoryFilterForm(initial={'category': category_filter})

        return context
    
class InventoryDetailView(LoginRequiredMixin, DetailView):
    model = Inventory
    template_name = 'inventory/inventory_detail.html'
    context_object_name = 'item'



    
    def get_queryset(self):
        return Inventory.objects.filter(user=self.request.user)
    
class InventoryCreateView(LoginRequiredMixin, CreateView):
    model = Inventory
    form_class = InventoryForm   
    template_name = 'inventory/add_inventory.html'
    success_url = reverse_lazy('inventory:inventory_list')

    def form_valid(self, form):
        form.instance.user =  self.request.user
        messages.success(self.request,'🎉 Məhsul uğurla əlavə edildi!')
        return super().form_valid(form)
    
class InventoryUpdateView(LoginRequiredMixin,UpdateView):
    
    model = Inventory
    form_class = InventoryForm
    template_name = 'inventory/edit_inventory.html'
    context_object_name = 'item'

    def get_queryset(self):
        return Inventory.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        messages.success(self.request,'✅ Məhsul məlumatları uğurla yeniləndi!')
        return reverse_lazy('inventory:inventory_detail', kwargs={'pk': self.object.pk})

class InventoryDeleteView(LoginRequiredMixin,DeleteView):
    model = Inventory
    template_name = 'inventory/delete_inventory.html'
    success_url = reverse_lazy('inventory:inventory_list')

    def get_queryset(self):
        return Inventory.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        
        messages.success(request, '🗑️ Məhsul uğurla silindi!')
        return super().delete(request, *args, **kwargs)


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
                return redirect('inventory:inventory_detail', pk=item.id)
            else:
                messages.error(request, 'Keçərsiz miqdar!')
        except (ValueError, TypeError):
            messages.error(request, 'Xətalı miqdar!')
    
    return render(request, 'inventory/track_usage.html', {'item': item})

@login_required
def low_stock(request):
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
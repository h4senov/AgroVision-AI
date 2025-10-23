from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from . models import Field
from .forms import FieldForm, FieldFilterForm, FieldSearchForm
from plants.models import Plant
from django.db.models import Sum , Count
from django.utils import timezone
from datetime import timedelta
from django.template.defaulttags import register

@login_required
def dashboard(request):
    fields = Field.objects.filter(user = request.user)
    plants = Plant.objects.filter(user = request.user)

    total_fields = fields.count()
    total_plants = plants.count()
    total_farm_area = fields.aggregate(total=Sum('area_hectares'))['total'] or 0
    total_plant_area = plants.aggregate(total=Sum('area_hectares'))['total'] or 0

    active_plants = plants.filter(status='active')
    active_plants_count = active_plants.count()

    next_week = timezone.now().date() + timedelta(days=7)
    upcoming_harvests = active_plants.filter(
        expected_harvest_date__lte=next_week,
        expected_harvest_date__gte=timezone.now().date()
    ).count()

    plant_distribution = plants.values('plant_type').annotate(
        count=Count('id'),
        total_area=Sum('area_hectares')
    ).order_by('-count')

    recent_plants = plants.order_by('-created_at')[:5]

    context = {
        'total_fields': total_fields,
        'total_plants': total_plants,
        'total_farm_area': total_farm_area,
        'total_plant_area': total_plant_area,
        'active_plants_count': active_plants_count,
        'upcoming_harvests': upcoming_harvests,
        'plant_distribution': plant_distribution,
        'recent_plants': recent_plants,
    }

    return render(request, 'dashboard.html', context)


@login_required
def field_list(request):
    fields = Field.objects.filter(user=request.user)

    search_query = request.GET.get('search','')
    soil_type_filter = request.GET.get('soil_type','')

    min_area = request.GET.get('min_area','')
    max_area = request.GET.get('max_area','')

    created_after = request.GET.get('created_after','')
    created_before = request.GET.get('created_before','')

    if created_after:
        fields = fields.filter(created_at__date__gte=created_after)
    if created_before:
        fields = fields.filter(created_at__date__lte=created_before)

    if search_query:
        fields = fields.filter(name__icontains=search_query)

    if soil_type_filter:
        fields = fields.filter(soil_type=soil_type_filter)

    if min_area:
        fields = fields.filter(area_hectares__gte=min_area)

    if max_area:
        fields = fields.filter(area_hectares__lte=max_area)  


    search_form = FieldSearchForm(initial={'search':search_query})        
    filter_form = FieldFilterForm(initial={
        'soil_type': soil_type_filter,
        'min_area': min_area,
        'max_area': max_area
    })  

    context = {
        'fields': fields,
        'search_form': search_form,
        'filter_form': filter_form
    }

    return render(request, 'fields/field_list.html', context)


@register.filter
def dict_key(d, key):
    """Dictionary-dən key-ə görə value almaq üçün"""
    return d.get(key, '')


@login_required
def field_detail(request, field_id):
    
    field = get_object_or_404(Field, id=field_id, user=request.user)

    plants = field.plants.all()

    total_plants = plants.count()
    
    active_plants  = plants.filter(status='active').count()

    total_area =  plants.aggregate(total=Sum('area_hectares'))['total'] or 0

     

    context = {

        'field': field,
        'plants': plants,
        'total_plants': total_plants,
        'active_plants': active_plants,
        'total_area': total_area,
    }



    return render(request, 'fields/field_detail.html', context)

@login_required
def add_field(request):
    if request.method == 'POST':
        form = FieldForm(request.POST)
        if form.is_valid():
            field = form.save(commit=False)
            field.user = request.user  
            field.save()
            return redirect('field_list')
    else:
        form = FieldForm()
    
    return render(request, 'fields/add_field.html', {'form': form})

@login_required
def edit_field(request, field_id):
   
    field = get_object_or_404(Field, id=field_id, user=request.user)
    
    if request.method == 'POST':
        form = FieldForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            return redirect('field_detail', field_id=field.id)
    else:
        form = FieldForm(instance=field)
    
    return render(request, 'fields/edit_field.html', {'form': form, 'field': field})

@login_required
def delete_field(request, field_id):
     
    field = get_object_or_404(Field, id=field_id, user=request.user)
    
    if request.method == 'POST':
        field.delete()
        return redirect('field_list')
    
    return render(request, 'fields/delete_field.html', {'field': field})

def home(request):
    
    if request.user.is_authenticated:
        total_fields = Field.objects.filter(user=request.user).count()
        total_plants = Plant.objects.filter(user=request.user).count()
    else:
        total_fields = 0
        total_plants = 0
    
    context = {
        'total_fields': total_fields,
        'total_plants': total_plants,
    }
    
    return render(request, 'home.html', context)


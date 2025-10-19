from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from . models import Field
from .forms import FieldForm
from plants.models import Plant
from django.db.models import Sum , Count
from django.utils import timezone
from datetime import timedelta
 
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
    return render(request, 'fields/field_list.html', {'fields': fields})



@login_required
def field_detail(request, field_id):
    
    field = get_object_or_404(Field, id=field_id, user=request.user)

    plants = field.plants.all()

    total_plants = plants.count()
    
    active_plants  = plants.filter(status='active').count()

    total_area =  plants.aggregete(total=Sum('area_hectares'))['total'] or 0

     

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
    return render(request, 'home.html')
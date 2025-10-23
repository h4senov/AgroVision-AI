from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Plant
from .forms import PlantForm,PlantFilterForm,PlantSearchForm
from fields.models import Field

 

@login_required
def plant_list(request):
    plants = Plant.objects.filter(user=request.user).select_related('field') # select relatedi silb test edersen

    search_query = request.GET.get('search','')
    plant_type_filter = request.GET.get('plant_type','')
    growth_stage_filter = request.GET.get('growth_stage','')
    status_filter = request.GET.get('status','')


    if search_query:
        plants = plants.filter(variety__icontains=search_query)

    if plant_type_filter:
        plants = plants.filter(plant_type=plant_type_filter)    

    if growth_stage_filter:
        plants = plants.filter(growth_stage=growth_stage_filter)

    if status_filter:
        plants = plants.filter(status=status_filter)


    search_form = PlantSearchForm(initial={'search' : search_query})

    filter_form = PlantFilterForm(initial={
        'plant_type': plant_type_filter,
        'growth_stage': growth_stage_filter,
        'status': status_filter
    })

    context = {
        'plants': plants,
        'search_form': search_form,
        'filter_form': filter_form,
    }

    return render(request, 'plants/plant_list.html', context)


@login_required
def plant_detail(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id, user=request.user)
    return render(request, 'plants/plant_detail.html', {'plant': plant})

@login_required
def add_plant(request):
    if request.method == 'POST':
        form = PlantForm(request.POST)
        if form.is_valid():
            plant = form.save(commit=False)
            plant.user = request.user
            plant.save()
            messages.success(request, 'Bitki uğurla əlavə edildi!')
            return redirect('plant_list')
    else:
        form = PlantForm()
        # Yalnız current user-ın sahələrini göstər
        form.fields['field'].queryset = Field.objects.filter(user=request.user)
    
    return render(request, 'plants/add_plant.html', {'form': form})

@login_required
def edit_plant(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id, user=request.user)
    
    if request.method == 'POST':
        form = PlantForm(request.POST, instance=plant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bitki məlumatları uğurla yeniləndi!')
            return redirect('plant_detail', plant_id=plant.id)
    else:
        form = PlantForm(instance=plant)
        form.fields['field'].queryset = Field.objects.filter(user=request.user)
    
    return render(request, 'plants/edit_plant.html', {'form': form, 'plant': plant})

@login_required
def delete_plant(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id, user=request.user)
    
    if request.method == 'POST':
        plant.delete()
        messages.success(request, 'Bitki uğurla silindi!')
        return redirect('plant_list')
    
    return render(request, 'plants/delete_plant.html', {'plant': plant})

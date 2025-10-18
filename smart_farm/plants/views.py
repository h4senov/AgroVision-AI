from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Plant
from .forms import PlantForm
from fields.models import Field

# Create your views here.

@login_required
def plant_list(request):
    plants = Plant.objects.filter(user=request.user).select_related('field')
    return render(request, 'plants/plant_list.html', {'plants': plants})

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

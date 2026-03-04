from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Plant , PlantManager
from .forms import PlantForm,PlantFilterForm,PlantSearchForm
from fields.models import Field
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

class PlantPredictionView(LoginRequiredMixin, DetailView):
    model = Plant
    template_name = 'plants/harvest_prediction.html'
    context_object_name = 'plant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prediction'] = Plant.objects.predict_harvest_time(self.object.id)
        return context

    def get_queryset(self):
        return Plant.objects.filter(user=self.request.user)
 

@login_required
def plant_list(request):
    
    query = request.GET.get('search','')
    filters = {
        'plant_type': request.GET.get('plant_type', ''),
        'growth_stage': request.GET.get('growth_stage', ''),
        'status': request.GET.get('status', ''),
    }
    
    plants = Plant.objects.search_plants(query, request.user, filters)

    search_form = PlantSearchForm(initial={'search': query})
    filter_form = PlantFilterForm(initial=filters)
    
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
        form = PlantForm(request.POST, request.FILES)
        if form.is_valid():
            plant = form.save(commit=False)
            plant.user = request.user
            plant.save()
            return redirect('plants:plant_list')
    else:
        form = PlantForm()
        form.fields['field'].queryset = Field.objects.filter(user=request.user)  # ← əlavə et
    return render(request, 'plants/add_plant.html', {'form': form})

@login_required
def edit_plant(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id, user=request.user)
    
    if request.method == 'POST':
        # request.FILES əlavə edildi ki, şəkil dəyişəndə bazaya yazılsın
        form = PlantForm(request.POST, request.FILES, instance=plant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bitki məlumatları uğurla yeniləndi!')
            return redirect('plants:plant_detail', plant_id=plant.id)
    else:
        form = PlantForm(instance=plant)
        # İstifadəçinin yalnız öz sahələrini görməsi üçün
        form.fields['field'].queryset = Field.objects.filter(user=request.user)
    
    return render(request, 'plants/edit_plant.html', {'form': form, 'plant': plant})
@login_required
def delete_plant(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id, user=request.user)
    
    if request.method == 'POST':
        plant.delete()
        messages.warning(request, f'{plant.get_plant_type_display()} bitkisi və bağlı məlumatlar silindi.')
        return redirect('plants:plant_list')
    
    return render(request, 'plants/delete_plant.html', {'plant': plant})
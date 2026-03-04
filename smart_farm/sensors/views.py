from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Sensor , SensorManager
from .forms import SensorForm, SensorFilterForm, SensorSearchForm
from fields.models import Field
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
class SensorDashboardView(LoginRequiredMixin, ListView):
    model = Sensor
    template_name = 'sensors/dashboard.html'
    context_object_name = 'sensors'

    def get_queryset(self):
        return Sensor.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sensors = context['sensors']
        rt_data = Sensor.objects.get_real_time_data(
            list(sensors.values_list('id', flat=True))
        )
        
        context['combined'] = [
            {'sensor': s, 'rt': rt_data.get(s.id, {})} for s in sensors
        ]
        return context




@login_required
def sensor_list(request):
    query = request.GET.get('search','')

    filters = {
        'sensor_type': request.GET.get('sensor_type',''),
        'is_active' : request.GET.get('status',''),
        'battery_level' : request.GET.get('battery_level',''),
    }

    sensors =   Sensor.objects.search_sensor(query, request.user, filters)
    

    search_form = SensorSearchForm(initial={'search': query}) 
    filter_form = SensorFilterForm(initial=filters)


    context = {
        'sensors': sensors,
        'search_form': search_form,
        'filter_form': filter_form,
    }
    
    return render(request, 'sensors/sensor_list.html', context)


@login_required
def sensor_detail(request, sensor_id):
    sensor = get_object_or_404(Sensor, id=sensor_id, user=request.user)
    readings = sensor.readings.all()[:10]  
    
    context = {
        'sensor': sensor,
        'readings': readings,
    }
    return render(request, 'sensors/sensor_detail.html', context)

@login_required
def add_sensor(request):
    if request.method == 'POST':
        form = SensorForm(request.POST)
        if form.is_valid():
            sensor = form.save(commit=False)
            sensor.user = request.user
            sensor.save()
            messages.success(request, 'Sensor uğurla əlavə edildi!')
            return redirect('sensors:sensor_list')
    else:
        form = SensorForm()
        
        form.fields['field'].queryset = Field.objects.filter(user=request.user)

    
    return render(request, 'sensors/add_sensor.html', {'form': form})

@login_required
def edit_sensor(request, sensor_id):
    sensor = get_object_or_404(Sensor, id=sensor_id, user=request.user)
    
    if request.method == 'POST':
        form = SensorForm(request.POST, instance=sensor)  
        if form.is_valid():
            form.save()
            messages.success(request, 'Sensor məlumatları uğurla yeniləndi!')
            return redirect('sensors:sensor_detail', sensor_id=sensor.id)
    else:
        form = SensorForm(instance=sensor)
        form.fields['field'].queryset = Field.objects.filter(user=request.user)
    
    return render(request, 'sensors/edit_sensor.html', {'form': form, 'sensor': sensor})

@login_required
def delete_sensor(request, sensor_id):
    sensor = get_object_or_404(Sensor, id=sensor_id, user=request.user)
    
    if request.method == 'POST':
        sensor.delete()
        messages.success(request, 'Sensor uğurla silindi!')
        return redirect('sensors:sensor_list')
    
    return render(request, 'sensors/delete_sensor.html', {'sensor': sensor})

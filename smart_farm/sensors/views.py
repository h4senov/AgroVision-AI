from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Sensor  
from .forms import SensorForm, SensorFilterForm, SensorSearchForm
from fields.models import Field
 
@login_required
def sensor_list(request):
    sensors = Sensor.objects.filter(user= request.user).select_related('field')


    search_query = request.GET.get('search','')
    sensor_type_filter = request.GET.get('sensor_type','')
    status_filter = request.GET.get('status', '')
    battery_level_filter = request.GET.get('battery_level', '')

    if search_query:
        sensors = sensors.filter(
            Q(name__icontains=search_query) | 
            Q(sensor_code__icontains=search_query)
        )
    
    if sensor_type_filter:
        sensors = sensors.filter(sensor_type=sensor_type_filter)
        
    if status_filter:
        if status_filter == 'active':
            sensors = sensors.filter(is_active=True)
        elif status_filter == 'inactive':
            sensors = sensors.filter(is_active=False)
    
    if battery_level_filter:
        if battery_level_filter == 'high':
            sensors = sensors.filter(battery_level__gt=70)
        elif battery_level_filter == 'medium':
            sensors = sensors.filter(battery_level__range=(30, 70))
        elif battery_level_filter == 'low':
            sensors = sensors.filter(battery_level__lt=30)


    search_form = SensorSearchForm(initial={'search': search_query}) 
    filter_form = SensorFilterForm(initial={ 
        'sensor_type': sensor_type_filter,
        'status': status_filter,
        'battery_level': battery_level_filter
    })

    context = {
        'sensors': sensors,
        'search_form': search_form,
        'filter_form': filter_form,
        'search_query': search_query,
        'sensor_type_filter': sensor_type_filter,
        'status_filter': status_filter,
        'battery_level_filter': battery_level_filter,
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
            return redirect('sensor_list')
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
            return redirect('sensor_detail', sensor_id=sensor.id)
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
        return redirect('sensor_list')
    
    return render(request, 'sensors/delete_sensor.html', {'sensor': sensor})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from sensors.models import Sensor
from . models import Field
from .forms import FieldForm, FieldFilterForm, FieldSearchForm
from plants.models import Plant
from django.db.models import Sum , Count
from django.utils import timezone
from datetime import timedelta
from django.template.defaulttags import register
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

class FieldMetricsView(LoginRequiredMixin, DetailView):
    model = Field
    template_name = 'fields/field_metrics.html'
    context_object_name = 'field'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['metrics'] = Field.objects.calculate_field_metrics(self.object.id)
        return context

    def get_queryset(self):
        return Field.objects.filter(user=self.request.user)



@login_required
def field_list(request):
    query = request.GET.get('search','')
    filters ={
        'soil_type': request.GET.get('soil_type', ''),
        'min_area': request.GET.get('min_area', ''),
        'max_area': request.GET.get('max_area', ''),
    }

    fields = Field.objects.search_fields(query, request.user, filters)    
    search_form = FieldSearchForm(initial={'search': query})
    filter_form = FieldFilterForm(initial=filters)

    context ={
        'fields': fields,
        'search_form': search_form,
        'filter_form': filter_form
    }

    return render(request, 'fields/field_list.html', context)




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
            return redirect('fields:field_list')
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
            return redirect('fields:field_detail', field_id=field.id)
    else:
        form = FieldForm(instance=field)
    
    return render(request, 'fields/edit_field.html', {'form': form, 'field': field})

@login_required
def delete_field(request, field_id):
     
    field = get_object_or_404(Field, id=field_id, user=request.user)
    
    if request.method == 'POST':
        field.delete()
        return redirect('fields:field_list')
    
    return render(request, 'fields/delete_field.html', {'field': field})






from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from . models import Field
from .forms import FieldForm
 
@login_required
def field_list(request):
 
    fields = Field.objects.filter(user=request.user)
    return render(request, 'fields/field_list.html', {'fields': fields})

@login_required
def field_detail(request, field_id):
    
    field = get_object_or_404(Field, id=field_id, user=request.user)
    return render(request, 'fields/field_detail.html', {'field': field})

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
from django.shortcuts import render, get_object_or_404, redirect
from . models import Field
from .forms import FieldForm
# Create your views here.


def field_list(request):
    fields = Field.objects.all()
    return render(request, 'fields/field_list.html', {'fields':fields})


def field_detail(request,field_id):
    field = get_object_or_404(Field, id=field_id)
    return render(request,'fields/field_detail.html',{'field': field})

def add_field(request):
    if request.method == 'POST':
        form = FieldForm(request.POST)
        if form.is_valid():
            field =  form.save(commit=False)
            field.user =  request.user 
            field.save()
            return redirect('field_list')
    else:
        form = FieldForm()

    return render(request,'fields/add_field.html', {'form':form})
     

def edit_field(request, field_id):
    field = get_object_or_404(Field, id = field_id)
    
    if request.method == 'POST':
        form = FieldForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            return redirect('field_detail', {'field':field})
    else:
        form = FieldForm(instance=field)
    
    return render(request, 'fields/edit_field.html', {'form': form, 'field': field})


def delete_field(request, field_id):
    field = get_object_or_404(Field, id=field_id)
    
    if request.method == 'POST':
        field.delete()
        return redirect('field_list')
    
    return render(request, 'fields/delete_field.html', {'field': field})

def home(request):
    return render(request, 'home.html')
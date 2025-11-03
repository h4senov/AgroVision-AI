from django.shortcuts import render, redirect 
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import CustomUser

# Create your views here.

def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('fields:field_list')
    else :
        form =CustomUserCreationForm()
    return render(request,'users/register.html',{'form' : form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('fields:field_list')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'users/login.html')
        
 

def user_logout(request):
    logout(request)
    return redirect('core:home')


@login_required
def user_profile(request):
    return render(request, 'users/profile.html', {'user': request.user})

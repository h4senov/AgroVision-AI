from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage
from .forms import ContactForm # Bunu forms.py-da yaratmaq lazımdır

# Statik səhifələr
def about_general(request):
    return render(request, 'pages/about_general.html')

def about_goals(request):
    return render(request, 'pages/about_goals.html')

def about_success(request):
    return render(request, 'pages/about_success.html')

def more_info(request):
    return render(request, 'pages/more_info.html')


# Əlaqə səhifəsi
def contact_index(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mesajınız qəbul edildi. Təşəkkürlər!")
            return redirect('pages:contact_index')
    else:
        form = ContactForm()
    
    return render(request, 'pages/contact.html', {'form': form})
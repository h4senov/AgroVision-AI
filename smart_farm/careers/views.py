from django.shortcuts import render, redirect, get_object_or_404
from .models import Vacancy, Application
from .forms import VacancyApplicationForm
from django.contrib import messages

def career_list(request):
    # Aktiv vakansiyaları gətiririk
    vacancies = Vacancy.objects.filter(is_active=True).order_by('-created_at')
    
    context = {
        'vacancies': vacancies,
    }
    return render(request, 'careers/career_list.html', context)

def career_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    
    if request.method == 'POST':
        form = VacancyApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.save()
            messages.success(request, "Müraciətiniz uğurla göndərildi!")
            return redirect('careers:career_list')
    else:
        form = VacancyApplicationForm()

    context = {
        'vacancy': vacancy,
        'form': form
    }
    return render(request, 'careers/career_detail.html', context)
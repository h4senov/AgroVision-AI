
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import WeatherData
from .forms import WeatherDataForm
class WeatherDataListView(LoginRequiredMixin, ListView):
    model = WeatherData
    template_name = 'weather/weather_list.html'
    context_object_name = 'weather_data'

    def get(self, request, *args, **kwargs):
        from fields.models import Field
        from .utils import fetch_weather_for_field
        fields = Field.objects.filter(
            user=request.user
        ).exclude(location__isnull=True).exclude(location='')
        for field in fields:
            fetch_weather_for_field(field)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
      
        from datetime import date
        return WeatherData.objects.filter(
            field__user=self.request.user,
            weather_date=date.today()
        ).select_related('field')


class WeatherDataDetailView(LoginRequiredMixin, DetailView):
    model = WeatherData
    template_name = 'weather/weather_detail.html'
    context_object_name = 'weather'

    def get_queryset(self):
        return WeatherData.objects.filter(field__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
         
        from datetime import date, timedelta
        week_data = WeatherData.objects.filter(
            field=self.object.field,
            weather_date__gte=date.today() - timedelta(days=6)
        ).order_by('weather_date')
        context['week_data'] = week_data
        return context

class WeatherDataCreateView(LoginRequiredMixin, CreateView):
    model = WeatherData
    form_class = WeatherDataForm
    template_name = 'weather/weather_form.html'
    success_url = reverse_lazy('weather:weather_list')

    def form_valid(self, form):
        print("Form valid:", form.is_valid())
        print("Form errors:", form.errors) 
        messages.success(self.request, '🌤️ Hava məlumatı uğurla əlavə edildi!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class WeatherDataUpdateView(LoginRequiredMixin, UpdateView):
    model = WeatherData
    form_class = WeatherDataForm
    template_name = 'weather/weather_form.html'
    context_object_name = 'weather'

    def get_success_url(self):
        messages.success(self.request, '✅ Hava məlumatı uğurla yeniləndi!')
        return reverse_lazy('weather:weather_detail', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        return WeatherData.objects.filter(field__user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class WeatherDataDeleteView(LoginRequiredMixin, DeleteView):
    model = WeatherData
    template_name = 'weather/weather_delete.html'
    success_url = reverse_lazy('weather:weather_list')
    context_object_name = 'weather'

    def get_queryset(self):
        return WeatherData.objects.filter(field__user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, '🗑️ Hava məlumatı uğurla silindi!')
        return super().delete(request, *args, **kwargs)
    
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from fields.models import Field
from .utils import fetch_weather_for_field

@login_required
def sync_weather(request):
    """İstifadəçinin bütün sahələri üçün hava datasını çəkir"""
    fields = Field.objects.filter(user=request.user, location__isnull=False).exclude(location='')
    count = 0
    for field in fields:
        result = fetch_weather_for_field(field)
        if result:
            count += 1
    messages.success(request, f'{count} sahə üçün hava datası yeniləndi! ✅')
    return redirect('weather:weather_list')    
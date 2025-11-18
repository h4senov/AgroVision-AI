
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
    paginate_by = 10

    def get_queryset(self):
        return WeatherData.objects.filter(
            field__user=self.request.user
            ).select_related('field').order_by('-weather_date')

class WeatherDataDetailView(LoginRequiredMixin, DetailView):
    model = WeatherData
    template_name = 'weather/weather_detail.html'
    context_object_name = 'weather'

    def get_queryset(self):
        return WeatherData.objects.filter(field__user=self.request.user)

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
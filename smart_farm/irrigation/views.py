from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import IrrigationSchedule
from .forms import IrrigationScheduleForm
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone

from plants.models import Plant
from django.http import JsonResponse


class IrrigationListView(LoginRequiredMixin, ListView):
    model = IrrigationSchedule
    template_name = 'irrigation/irrigation_list.html'
    context_object_name = 'schedules'
    paginate_by = 10  # Səhifələmə (Pagination) avtomatik işləyəcək

    def get_queryset(self):
        """
        Manager-də yazdığımız search_irrigation metodunu burada çağırırıq.
        """
        query = self.request.GET.get('q', '')
        filters = {
            'irrigation_type': self.request.GET.get('type'),
            'status': self.request.GET.get('status'),
            'start_date': self.request.GET.get('date_from'),
            'end_date': self.request.GET.get('date_to'),
            'field': self.request.GET.get('field_id'),
        }
        # Manager-i istifadə edirik
        return IrrigationSchedule.objects.search_irrigation(
            query=query, 
            user=self.request.user, 
            filters=filters
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 1. Bugünkü istehlak və növbəti suvarma (Bunlar okeydir)
        context['today_consumption'] = IrrigationSchedule.total_consumption_today(user)
        context['next_irrigation'] = IrrigationSchedule.next_upcoming_irrigation(user)
        
        # 2. Ümumi zonalar
        user_fields = user.fields.all()
        context['total_zones'] = user_fields.count()
        
        # 3. Aktiv zonalar (Statusu hazırda 'active' olanlar)
        context['active_zones_count'] = IrrigationSchedule.objects.filter(
            field__user=user, 
            status='active'
        ).values('field').distinct().count()
        
        # 4. PROBLEM ZONALAR (Xətanın həlli bura idi)
        # Sahənin özündə rütubət yoxdur deyə, son suvarma qeydindəki rütubətə baxırıq
        context['problem_zones'] = IrrigationSchedule.objects.filter(
            field__user=user,
            soil_moisture_level__lt=20  # Rütubəti 20-dən aşağı olan son qeydlər
        ).values('field').distinct().count()
        
        # Statik seçimlər
        context['irrigation_types'] = IrrigationSchedule.IRRIGATION_TYPE
        context['status_choices'] = IrrigationSchedule.STATUS_CHOICES
        
        return context

def load_plants(request):
    field_id = request.GET.get('field_id')
    plants = Plant.objects.filter(field_id=field_id).values('id', 'plant_type', 'variety')
    
    # Bitki adlarını oxunaqlı formata salırıq
    plant_list = []
    for p in plants:
        name = f"{p['plant_type']} - {p['variety']}" if p['variety'] else p['plant_type']
        plant_list.append({'id': p['id'], 'name': name})
        
    return JsonResponse(plant_list, safe=False)

class IrrigationCreateView(LoginRequiredMixin, CreateView):
    model = IrrigationSchedule
    form_class = IrrigationScheduleForm
    template_name = 'irrigation/irrigation_form.html'
    success_url = reverse_lazy('irrigation:irrigation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  
        return kwargs


class IrrigationUpdateView(LoginRequiredMixin, UpdateView):
    model = IrrigationSchedule
    form_class = IrrigationScheduleForm
    template_name = 'irrigation/irrigation_form.html'
    success_url = reverse_lazy('irrigation:irrigation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class IrrigationDeleteView(LoginRequiredMixin, DeleteView):
    model = IrrigationSchedule
    template_name = 'irrigation/irrigation_confirm_delete.html'
    success_url = reverse_lazy('irrigation:irrigation_list')



def complete_irrigation(request, pk):
    """Suvarmanı bir kliklə tamamlanmış kimi qeyd edir"""
    irrigation = get_object_or_404(IrrigationSchedule, pk=pk)
    irrigation.status = 'completed'
    irrigation.end_time = timezone.now().time() # Bitmə vaxtını avtomatik qeyd edir
    irrigation.save()
    return redirect('irrigation:irrigation_list')

def duplicate_irrigation(request, pk):
    """Mövcud suvarma qeydini kopyalayır və yeni tarixə atır"""
    old_obj = get_object_or_404(IrrigationSchedule, pk=pk)
    new_obj = old_obj
    new_obj.pk = None # Yeni ID yaransın deyə PK-nı sıfırlayırıq
    new_obj.irrigation_date = timezone.now().date() # Bu günə kopyalayır
    new_obj.status = 'planned' # Statusu sıfırlayır
    new_obj.save()
    return redirect('irrigation:irrigation_update', pk=new_obj.pk)

# views.py
from django.views.generic import DetailView

class IrrigationDetailView(LoginRequiredMixin, DetailView):
    model = IrrigationSchedule
    template_name = 'irrigation/irrigation_detail.html'
    context_object_name = 'object'
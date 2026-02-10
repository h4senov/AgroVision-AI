from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .forms import CustomUserCreationForm, CustomUserUpdateForm, CustomPasswordChangeForm, UserDeactivationForm
from .models import CustomUser

def admin_required(function):
    actual_decorator =  user_passes_test(
        lambda u: u.role == 'admin' or u.is_superuser,
        login_url='/users/login'
    )
    return actual_decorator(function)

# users/views.py

def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Backend-i dəqiqləşdiririk ki, login problemi olmasın
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, '🎉 Uğurla qeydiyyatdan keçdiniz!')
            return redirect('core:dashboard')
        else:
            # Form valid deyilsə, xəta mesajı verək
            messages.error(request, '❌ Zəhmət olmasa xətaları düzəldin.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# ============ AUTH VIEWS ============

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                user.last_login = timezone.now()
                user.save()
                messages.success(request, f'👋 Xoş gəldiniz, {user.username}!')
                return redirect('core:dashboard')
            else:
                messages.error(request, '❌ Hesabınız deaktiv edilib.')
        else:
            messages.error(request, '❌ Yanlış istifadəçi adı və ya şifrə.')
    
    return render(request, 'users/login.html')
        
 

def user_logout(request):
    logout(request)
    messages.info(request, '👋 Uğurla çıxış etdiniz.')
    return redirect('core:home')

# ============ PROFILE VIEWS ============

@login_required
def user_profile(request):
    user_stats = {
        'fields_count': request.user.get_fields_count(),
        'plants_count': request.user.get_plants_count(),
        'sensors_count': request.user.get_sensors_count(),
        'inventory_count': request.user.get_inventory_count(),
        'activity_level': request.user.get_activity_level(),
        'last_activity_days': request.user.get_last_activity_days(),
    }
    
    return render(request, 'users/profile.html', {
        'user': request.user,
        'user_stats': user_stats
    })

@login_required
def update_user_profile(request):
     
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Profil məlumatları uğurla yeniləndi!')
            return redirect('users:user_profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)
    
    return render(request, 'users/update_profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '✅ Şifrəniz uğurla dəyişdirildi!')
            return redirect('users:user_profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})


from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required  # Yalnız admin heyəti daxil ola bilsin
def deactivate_user(request, user_id):
    # Deaktiv ediləcək istifadəçini tapırıq
    target_user = get_object_or_404(CustomUser, id=user_id)
    
    # Admin özünü səhvən deaktiv etməsin deyə qoruma
    if target_user == request.user:
        messages.error(request, "Öz hesabınızı deaktiv edə bilməzsiniz!")
        return redirect('users:user_statistics')

    if request.method == 'POST':
        form = UserDeactivationForm(request.POST)
        if form.is_valid():
            # Məntiqi deaktivasiya
            target_user.is_active = False
            target_user.save()
            
            # Burada səbəbi log-a yaza və ya adminə bildiriş göndərə bilərsən
            reason = form.cleaned_data['deactivate_reason']
            
            messages.success(request, f"{target_user.username} uğurla deaktiv edildi. Səbəb: {reason}")
            return redirect('users:user_statistics')
    else:
        form = UserDeactivationForm()

    return render(request, 'users/deactivate_user.html', {
        'form': form,
        'user': target_user  # HTML-də istifadəçinin adını göstərmək üçün
    })
def terms_view(request):
    return render(request, 'users/terms.html')


@login_required
@admin_required
def activate_user(request, user_id):
    
    user_to_activate = get_object_or_404(CustomUser, id=user_id)
    
    user_to_activate.is_active = True
    user_to_activate.save()
    
    messages.success(request, f'✅ {user_to_activate.username} aktiv edildi.')
    return redirect('users:user_statistics')



class UserStatisticsListView(ListView):
    
    model = CustomUser
    template_name = 'users/user_statistics.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        
        return CustomUser.objects.annotate(
            fields_count=Count('fields', distinct=True),
            plants_count=Count('plant', distinct=True),
            sensors_count=Count('sensor', distinct=True),
            inventory_count=Count('inventory', distinct=True),
        ).select_related().order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        
        total_users = CustomUser.objects.count()
        active_users = CustomUser.objects.filter(is_active=True).count()
        inactive_users = total_users - active_users
        
        
        role_distribution = CustomUser.objects.values('role').annotate(
            count=Count('id'),
            active_count=Count('id', filter=Q(is_active=True))
        ).order_by('-count')
        
       
        recent_active_users = CustomUser.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        context.update({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'role_distribution': role_distribution,
            'recent_active_users': recent_active_users,
        })
        
        return context
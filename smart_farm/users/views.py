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
from .models import UserSession
def get_client_ip(request):
    """Real IP-ni al (proxy arxasında da işləyir)"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')



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

            # --- SESSİYA QEYDİNİ BURADA DA YARADIRIQ ---
            UserSession.objects.create(
                user=user, # yeni yaradılan user
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                city="Baku",
                browser=request.META.get('HTTP_USER_AGENT', '').split(' ')[0],
                device="Mobile" if "Mobile" in request.META.get('HTTP_USER_AGENT', '') else "Desktop"
            )
            # ------------------------------------------

            messages.success(request, '🎉 Uğurla qeydiyyatdan keçdiniz!')
            return redirect('core:dashboard')
        else:
            messages.error(request, '❌ Zəhmət olmasa xətaları düzəldin.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})
# ============ AUTH VIEWS ============ 
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')  
        
        user_obj = authenticate(request, username=username, password=password)
        
        if user_obj is not None:
            if user_obj.is_active:
                # 1. Giriş et
                login(request, user_obj)
                
                # 2. Sessiya müddətini nizamla (DÜZ YAZMISAN)
                if not remember: 
                    request.session.set_expiry(0)   
                else:
                    request.session.set_expiry(1209600) # 14 gün
                
                # 3. UserSession logunu YALNIZ uğurlu girişdən sonra yarat/yenilə
                
                UserSession.objects.create(
                    user=user_obj,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    city="Baku",  # Bura bərabərdir (=) olmalıdır
                    browser=request.META.get('HTTP_USER_AGENT', '').split(' ')[0], # bərabərdir (=)
                    device="Mobile" if "Mobile" in request.META.get('HTTP_USER_AGENT', '') else "Desktop" # bərabərdir (=)
                )
                            # 4. Son giriş vaxtını yenilə
                user_obj.last_login = timezone.now()
                user_obj.save()

                messages.success(request, f'👋 Xoş gəldiniz, {user_obj.username}!')
                return redirect('core:dashboard')
            else:
                messages.error(request, '❌ Hesabınız deaktivdir.')
        else:
            messages.error(request, '❌ İstifadəçi adı və ya şifrə yanlışdır.') 
            
    return render(request, 'users/login.html')
        
def all_user_sessions(request):
    # .all() yazırıq ki, hamı gəlsin
    sessions = UserSession.objects.all().select_related('user').order_by('-created_at')
    return render(request, 'users/all_sessions.html', {'sessions': sessions})


def user_logout(request):
    logout(request)
    messages.info(request, '👋 Uğurla çıxış etdiniz.')
    return redirect('core:home')

# ============ PROFILE VIEWS ============

@login_required
def user_profile(request):
    user_session = UserSession.objects.filter(user=request.user).first()

    recent_sessions = None
    if request.user.is_superuser:
        recent_sessions = UserSession.objects.select_related('user').order_by('-last_login')[:20]
    context = {
        'user_session':    user_session,
        'recent_sessions': recent_sessions,
        'fields_count': request.user.get_fields_count(),
        'plants_count': request.user.get_plants_count(),
        'sensors_count': request.user.get_sensors_count(),
        'inventory_count': request.user.get_inventory_count(),
        'activity_level': request.user.get_activity_level(),
        'last_activity_days': request.user.get_last_activity_days(),
    }
    
    return render(request, 'users/profile.html', context)

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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.generic import ListView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .forms import CustomUserCreationForm, CustomUserUpdateForm, CustomPasswordChangeForm, UserDeactivationForm
from .models import CustomUser, UserSession


# ════════════════════════════════════════
# YARDIMÇI
# ════════════════════════════════════════

def get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def parse_user_agent(ua):
    u = ua.lower()
    device  = 'Mobile' if any(x in u for x in ['mobile','android','iphone','ipad']) else ('Tablet' if 'tablet' in u else 'Desktop')
    os_name = ('Windows' if 'windows' in u else 'Android' if 'android' in u else 'iOS' if 'iphone' in u or 'ipad' in u else 'macOS' if 'mac' in u else 'Linux' if 'linux' in u else 'Digər')
    browser = ('Edge' if 'edg/' in u else 'Opera' if 'opr/' in u else 'Chrome' if 'chrome/' in u else 'Firefox' if 'firefox/' in u else 'Safari' if 'safari/' in u else 'Digər')
    is_bot  = any(x in u for x in ['bot','crawl','spider','slurp','wget','curl'])
    return {'device': device, 'os': os_name, 'browser': browser, 'is_bot': is_bot}


def save_session(request, user_obj=None):
    """
    FIX: update_or_create dublikat tapanda çökür.
    filter().first() + manual save işlətmək daha etibarlıdır.
    Eyni zamanda köhnə dublikatları da təmizləyir.
    """
    client_ip = get_client_ip(request)
    u_agent   = request.META.get('HTTP_USER_AGENT', '')[:500]
    curr_user = user_obj or (request.user if request.user.is_authenticated else None)
    ua_info   = parse_user_agent(u_agent)

    # Mövcud sessiyaları tap
    qs = UserSession.objects.filter(user=curr_user, ip_address=client_ip).order_by('-last_login')

    if qs.count() > 1:
        # Dublikatları sil, yalnız birincisi qalsın
        ids_to_delete = list(qs.values_list('id', flat=True)[1:])
        UserSession.objects.filter(id__in=ids_to_delete).delete()

    session = qs.first()

    if session:
        session.user_agent = u_agent
        session.browser    = ua_info['browser']
        session.os         = ua_info['os']
        session.device     = ua_info['device']
        session.is_bot     = ua_info['is_bot']
        session.save()          # auto_now=True → last_login özü yenilənir
    else:
        UserSession.objects.create(
            ip_address = client_ip,
            user       = curr_user,
            user_agent = u_agent,
            browser    = ua_info['browser'],
            os         = ua_info['os'],
            device     = ua_info['device'],
            is_bot     = ua_info['is_bot'],
        )


def admin_required(function):
    return user_passes_test(
        lambda u: u.role == 'admin' or u.is_superuser,
        login_url='/users/login'
    )(function)


# ════════════════════════════════════════
# AUTH
# ════════════════════════════════════════

def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            save_session(request, user)
            messages.success(request, '🎉 Uğurla qeydiyyatdan keçdiniz!')
            return redirect('core:dashboard')
        else:
            messages.error(request, '❌ Zəhmət olmasa xətaları düzəldin.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember')

        user_obj = authenticate(request, username=username, password=password)

        if user_obj is not None:
            if user_obj.is_active:
                login(request, user_obj)

                # Məni xatırla
                if not remember:
                    request.session.set_expiry(0)       # brauzer bağlananda bitir
                else:
                    request.session.set_expiry(1209600) # 14 gün

                save_session(request, user_obj)
                user_obj.last_login = timezone.now()
                user_obj.save(update_fields=['last_login'])

                messages.success(request, f'👋 Xoş gəldiniz, {user_obj.username}!')
                return redirect('core:dashboard')
            else:
                messages.error(request, '❌ Hesabınız deaktivdir.')
        else:
            messages.error(request, '❌ İstifadəçi adı və ya şifrə yanlışdır.')

    return render(request, 'users/login.html')


def user_logout(request):
    logout(request)
    messages.info(request, '👋 Uğurla çıxış etdiniz.')
    return redirect('core:home')


# ════════════════════════════════════════
# PROFILE
# ════════════════════════════════════════

@login_required
def user_profile(request):
    user         = request.user
    user_session = UserSession.objects.filter(user=user).order_by('-last_login').first()

    recent_sessions = None
    if user.is_superuser:
        recent_sessions = UserSession.objects.select_related('user').order_by('-last_login')[:20]

    context = {
        'user_session':    user_session,
        'recent_sessions': recent_sessions,
        'user_stats': {
            'fields_count':       user.get_fields_count(),
            'plants_count':       user.get_plants_count(),
            'sensors_count':      user.get_sensors_count(),
            'inventory_count':    user.get_inventory_count(),
            'activity_level':     user.get_activity_level(),
            'last_activity_days': user.get_last_activity_days(),
        },
    }
    return render(request, 'users/profile.html', context)


@login_required
def update_user_profile(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
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


# ════════════════════════════════════════
# ŞİFRƏ SIFIRLAMA — email + token əsaslı
# ════════════════════════════════════════

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


def password_reset_request(request):
    """İstifadəçi email daxil edir → link göndərilir"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email, is_active=True)
            uid   = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(
                f'/az/users/password-reset/{uid}/{token}/'
            )
            send_mail(
                subject='AgroVision — Şifrə Sıfırlama',
                message=f'Şifrənizi sıfırlamaq üçün bu linkə keçin:\n\n{reset_url}\n\nLink 24 saat etibarlıdır.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass  # Email mövcud olmasa belə eyni mesaj — security
        messages.success(request, '📧 Email ünvanınıza link göndərildi (əgər hesab varsa).')
        return redirect('users:password_reset_done')
    return render(request, 'users/password_reset.html')


def password_reset_done(request):
    return render(request, 'users/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    """Link keçərli isə yeni şifrə formu"""
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    valid = user is not None and default_token_generator.check_token(user, token)

    if request.method == 'POST' and valid:
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Şifrəniz uğurla yeniləndi! Daxil ola bilərsiniz.')
            return redirect('users:user_login')
    else:
        form = SetPasswordForm(user) if valid else None

    return render(request, 'users/password_reset_confirm.html', {
        'form': form, 'valid': valid
    })


# ════════════════════════════════════════
# ADMIN VIEWS
# ════════════════════════════════════════

@staff_member_required
def all_user_sessions(request):
    sessions = UserSession.objects.select_related('user').order_by('-last_login')
    return render(request, 'users/all_sessions.html', {'sessions': sessions})


@staff_member_required
def deactivate_user(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)
    if target_user == request.user:
        messages.error(request, "Öz hesabınızı deaktiv edə bilməzsiniz!")
        return redirect('users:user_statistics')
    if request.method == 'POST':
        form = UserDeactivationForm(request.POST)
        if form.is_valid():
            target_user.is_active = False
            target_user.save()
            messages.success(request, f"{target_user.username} deaktiv edildi.")
            return redirect('users:user_statistics')
    else:
        form = UserDeactivationForm()
    return render(request, 'users/deactivate_user.html', {'form': form, 'user': target_user})


def terms_view(request):
    return render(request, 'users/terms.html')


@login_required
@admin_required
def activate_user(request, user_id):
    u = get_object_or_404(CustomUser, id=user_id)
    u.is_active = True
    u.save()
    messages.success(request, f'✅ {u.username} aktiv edildi.')
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
        ).order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total   = CustomUser.objects.count()
        active  = CustomUser.objects.filter(is_active=True).count()
        context.update({
            'total_users':         total,
            'active_users':        active,
            'inactive_users':      total - active,
            'role_distribution':   CustomUser.objects.values('role').annotate(
                                       count=Count('id'),
                                       active_count=Count('id', filter=Q(is_active=True))
                                   ).order_by('-count'),
            'recent_active_users': CustomUser.objects.filter(
                                       last_login__gte=timezone.now() - timedelta(days=7)
                                   ).count(),
        })
        return context
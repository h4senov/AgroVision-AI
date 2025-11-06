from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.user_register, name='user_register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/update/', views.update_user_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
   
    path('statistics/', views.UserStatisticsListView.as_view(), name='user_statistics'),
    path('deactivate/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('activate/<int:user_id>/', views.activate_user, name='activate_user'),
]
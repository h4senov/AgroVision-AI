from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.about_general, name='about_general'),
    path('goals/', views.about_goals, name='about_goals'),
    path('success/', views.about_success, name='about_success'),
    path('more-info/', views.more_info, name='more_info'),
    path('contact/', views.contact_index, name='contact_index'),
]
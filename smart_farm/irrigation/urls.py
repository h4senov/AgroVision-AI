from django.urls import path
from . import views

app_name = 'irrigation'

urlpatterns = [
    path('', views.IrrigationListView.as_view(), name='irrigation_list'),
    path('add/', views.IrrigationCreateView.as_view(), name='irrigation_add'),
    path('<int:pk>/', views.IrrigationDetailView.as_view(), name='irrigation_detail'),
    path('<int:pk>/update/', views.IrrigationUpdateView.as_view(), name='irrigation_update'),
    path('<int:pk>/delete/', views.IrrigationDeleteView.as_view(), name='irrigation_delete'),
    path('ajax/load-plants/', views.load_plants, name='ajax_load_plants'),
]
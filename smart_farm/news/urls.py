from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('',               views.news_list,   name='news_list'),
    path('create/',        views.news_create, name='news_create'),
    path('<slug:slug>/',         views.news_detail, name='news_detail'),
    path('<slug:slug>/edit/',    views.news_update, name='news_update'),
    path('<slug:slug>/delete/',  views.news_delete, name='news_delete'),
]

 
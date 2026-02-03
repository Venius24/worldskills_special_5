"""
URL Configuration для приложения управления промоакциями
"""
from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('', views.promotion_list, name='list'),
    path('create/', views.promotion_create, name='create'),
    path('update/<int:pk>/', views.promotion_update, name='update'),
    path('delete/<int:pk>/', views.promotion_delete, name='delete'),
    path('conflict-wizard/', views.conflict_wizard, name='conflict_wizard'),
    path('wizard-action/', views.wizard_next_step, name='wizard_action'),
    path('api/<int:pk>/', views.get_promotion_data, name='api_detail'),
]
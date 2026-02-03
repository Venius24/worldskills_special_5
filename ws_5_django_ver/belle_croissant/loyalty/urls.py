"""
URL Configuration для приложения управления лояльностью
"""
from django.urls import path
from . import views

app_name = 'loyalty'

urlpatterns = [
    path('', views.loyalty_list, name='list'),
    path('customer/<int:customer_id>/', views.loyalty_detail, name='detail'),
    path('customer/<int:customer_id>/update-points/', views.loyalty_update_points, name='update_points'),
    path('customer/<int:customer_id>/recalculate/', views.loyalty_recalculate_points, name='recalculate'),
    path('customer/<int:customer_id>/confirm-recalculation/', views.loyalty_confirm_recalculation, name='confirm_recalculation'),
    path('customer/<int:customer_id>/redeem/', views.loyalty_redeem_reward, name='redeem'),
]
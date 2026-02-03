"""
URL Configuration для Mock API
"""
from django.urls import path
from . import views

app_name = 'api_mock'

urlpatterns = [
    # Customers
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:customer_id>/orders/', views.customer_orders, name='customer_orders'),
    
    # Products
    path('products/', views.products_list, name='products_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Orders
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]
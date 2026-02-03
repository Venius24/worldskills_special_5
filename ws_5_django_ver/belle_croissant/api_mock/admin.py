"""
Административная панель для Mock API
"""
from django.contrib import admin
from .models import Customer, Product, Order, OrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Админка для клиентов"""
    
    list_display = [
        'id', 'first_name', 'last_name', 'email', 
        'membership_status', 'total_spending', 'registration_date'
    ]
    list_filter = ['membership_status', 'registration_date']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['-id']
    
    fieldsets = (
        ('Личная информация', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Членство', {
            'fields': ('membership_status', 'total_spending')
        }),
        ('Метаданные', {
            'fields': ('registration_date',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['registration_date']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка для продуктов"""
    
    list_display = [
        'id', 'name', 'category', 'price', 'is_available'
    ]
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'price')
        }),
        ('Дополнительно', {
            'fields': ('description', 'is_available')
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для заказов"""
    
    list_display = [
        'id', 'customer', 'order_date', 'status', 'total_amount'
    ]
    list_filter = ['status', 'order_date']
    search_fields = ['customer__email', 'customer__first_name', 'customer__last_name']
    ordering = ['-order_date']
    
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('customer', 'status', 'total_amount')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'order_date')
        }),
    )
    
    readonly_fields = ['order_date']
    
    inlines = []


class OrderItemInline(admin.TabularInline):
    """Inline для элементов заказа"""
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


# Добавляем inline к OrderAdmin
OrderAdmin.inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Админка для элементов заказа"""
    
    list_display = [
        'id', 'order', 'product', 'quantity', 'unit_price', 'subtotal'
    ]
    list_filter = ['order__order_date']
    search_fields = ['product__name', 'order__id']
    ordering = ['-order__order_date']
    
    readonly_fields = ['subtotal']
"""
Административная панель для промоакций
"""
from django.contrib import admin
from .models import Promotion, PromotionConflict


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Админка для промоакций"""
    
    list_display = [
        'id', 'name', 'discount_type', 'discount_value', 
        'start_date', 'end_date', 'priority', 'is_active'
    ]
    list_filter = ['discount_type', 'priority', 'start_date', 'end_date']
    search_fields = ['name', 'applicable_products']
    ordering = ['-priority', '-start_date']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'discount_type', 'discount_value')
        }),
        ('Применение', {
            'fields': ('applicable_products', 'minimum_order_value', 'priority')
        }),
        ('Период действия', {
            'fields': ('start_date', 'end_date')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def is_active(self, obj):
        """Отображение активности промоакции"""
        return obj.is_active()
    is_active.boolean = True
    is_active.short_description = 'Активна'


@admin.register(PromotionConflict)
class PromotionConflictAdmin(admin.ModelAdmin):
    """Админка для конфликтов промоакций"""
    
    list_display = [
        'id', 'promotion1', 'promotion2', 
        'overlap_start', 'overlap_end', 'resolved'
    ]
    list_filter = ['resolved', 'created_at']
    search_fields = ['promotion1__name', 'promotion2__name']
    ordering = ['-created_at']
    
    readonly_fields = ['created_at']
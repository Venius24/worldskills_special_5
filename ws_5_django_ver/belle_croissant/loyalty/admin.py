"""
Административная панель для программы лояльности
"""
from django.contrib import admin
from .models import LoyaltyProgram, LoyaltyTransaction, RewardRedemption


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    """Админка для программы лояльности"""
    
    list_display = [
        'customer_id', 'loyalty_points', 'membership_status', 
        'registration_date', 'can_redeem_rewards'
    ]
    list_filter = ['membership_status', 'registration_date']
    search_fields = ['customer_id']
    ordering = ['-loyalty_points']
    
    fieldsets = (
        ('Информация о клиенте', {
            'fields': ('customer_id', 'membership_status')
        }),
        ('Баллы лояльности', {
            'fields': ('loyalty_points', 'last_points_calculation')
        }),
        ('Метаданные', {
            'fields': ('registration_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'registration_date']
    
    def can_redeem_rewards(self, obj):
        """Может ли обменять награды"""
        return obj.can_redeem_rewards()
    can_redeem_rewards.boolean = True
    can_redeem_rewards.short_description = 'Может обменять'


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    """Админка для транзакций лояльности"""
    
    list_display = [
        'id', 'loyalty_program', 'transaction_type', 
        'points', 'order_id', 'created_at'
    ]
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['loyalty_program__customer_id', 'order_id', 'description']
    ordering = ['-created_at']
    
    readonly_fields = ['created_at']


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    """Админка для обменов наград"""
    
    list_display = [
        'id', 'loyalty_program', 'reward_type', 
        'points_spent', 'promotion_id', 'redeemed_at'
    ]
    list_filter = ['reward_type', 'redeemed_at']
    search_fields = ['loyalty_program__customer_id']
    ordering = ['-redeemed_at']
    
    readonly_fields = ['redeemed_at']
"""
Модели для приложения управления программой лояльности
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class LoyaltyProgram(models.Model):
    """Модель программы лояльности клиента"""
    
    MEMBERSHIP_STATUS_CHOICES = [
        ('Basic', 'Basic'),
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
    ]
    
    customer_id = models.IntegerField(
        'ID клиента',
        unique=True,
        primary_key=True
    )
    loyalty_points = models.IntegerField(
        'Баллы лояльности',
        default=0,
        validators=[MinValueValidator(0)]
    )
    membership_status = models.CharField(
        'Статус членства',
        max_length=20,
        choices=MEMBERSHIP_STATUS_CHOICES,
        default='Basic'
    )
    registration_date = models.DateField(
        'Дата регистрации',
        auto_now_add=True
    )
    last_points_calculation = models.DateTimeField(
        'Последний расчёт баллов',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        db_table = 'loyalty_program'
        verbose_name = 'Программа лояльности'
        verbose_name_plural = 'Программы лояльности'
        ordering = ['-loyalty_points']
    
    def __str__(self):
        return f"Клиент #{self.customer_id} - {self.membership_status} ({self.loyalty_points} баллов)"
    
    def get_points_multiplier(self):
        """Получить множитель баллов в зависимости от уровня"""
        multipliers = {
            'Basic': 10,
            'Silver': 12,
            'Gold': 15,
        }
        return multipliers.get(self.membership_status, 10)
    
    def can_redeem_rewards(self):
        """Проверка возможности обмена баллов на награды"""
        return self.loyalty_points >= 1000
    
    def get_next_membership_level(self):
        """Получить следующий уровень членства"""
        levels = ['Basic', 'Silver', 'Gold']
        current_index = levels.index(self.membership_status)
        if current_index < len(levels) - 1:
            return levels[current_index + 1]
        return None
    
    def can_upgrade_membership(self):
        """Проверка возможности повышения уровня"""
        return self.get_next_membership_level() is not None
    
    def is_anniversary(self):
        """Проверка годовщины регистрации"""
        today = timezone.now().date()
        return (today.month == self.registration_date.month and 
                today.day == self.registration_date.day)


class LoyaltyTransaction(models.Model):
    """Модель транзакции баллов лояльности"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('earn', 'Начисление'),
        ('redeem', 'Списание'),
        ('adjustment', 'Корректировка'),
        ('bonus', 'Бонус'),
    ]
    
    loyalty_program = models.ForeignKey(
        LoyaltyProgram,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        'Тип транзакции',
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES
    )
    points = models.IntegerField('Баллы')
    order_id = models.IntegerField('ID заказа', null=True, blank=True)
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)
    
    class Meta:
        db_table = 'loyalty_transactions'
        verbose_name = 'Транзакция лояльности'
        verbose_name_plural = 'Транзакции лояльности'
        ordering = ['-created_at']
    
    def __str__(self):
        sign = '+' if self.points > 0 else ''
        return f"{self.loyalty_program.customer_id}: {sign}{self.points} баллов ({self.get_transaction_type_display()})"


class RewardRedemption(models.Model):
    """Модель обмена баллов на награды"""
    
    REWARD_TYPE_CHOICES = [
        ('fixed_discount', 'Скидка 5€'),
        ('percentage_discount', 'Скидка 10%'),
        ('membership_upgrade', 'Повышение уровня'),
    ]
    
    loyalty_program = models.ForeignKey(
        LoyaltyProgram,
        on_delete=models.CASCADE,
        related_name='redemptions'
    )
    reward_type = models.CharField(
        'Тип награды',
        max_length=30,
        choices=REWARD_TYPE_CHOICES
    )
    points_spent = models.IntegerField('Потрачено баллов', default=1000)
    promotion_id = models.IntegerField('ID промоакции', null=True, blank=True)
    redeemed_at = models.DateTimeField('Дата обмена', auto_now_add=True)
    
    class Meta:
        db_table = 'reward_redemptions'
        verbose_name = 'Обмен награды'
        verbose_name_plural = 'Обмены наград'
        ordering = ['-redeemed_at']
    
    def __str__(self):
        return f"Клиент #{self.loyalty_program.customer_id}: {self.get_reward_type_display()}"
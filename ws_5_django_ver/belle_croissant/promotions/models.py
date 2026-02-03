"""
Модели для приложения управления промоакциями
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Promotion(models.Model):
    """Модель промоакции"""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Процентная скидка'),
        ('fixed', 'Фиксированная сумма'),
    ]
    
    name = models.CharField('Название', max_length=255)
    discount_type = models.CharField(
        'Тип скидки',
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES
    )
    discount_value = models.DecimalField(
        'Размер скидки',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    applicable_products = models.TextField(
        'Применимые продукты',
        help_text='ID продуктов через запятую'
    )
    start_date = models.DateTimeField('Дата начала')
    end_date = models.DateTimeField('Дата окончания')
    minimum_order_value = models.DecimalField(
        'Минимальная сумма заказа',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    priority = models.IntegerField(
        'Приоритет',
        default=1,
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        db_table = 'promotions'
        verbose_name = 'Промоакция'
        verbose_name_plural = 'Промоакции'
        ordering = ['-priority', '-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.get_discount_display()})"
    
    def get_discount_display(self):
        """Отображение скидки"""
        if self.discount_type == 'percentage':
            return f"{self.discount_value}%"
        return f"{self.discount_value}€"
    
    def get_applicable_products_list(self):
        """Получить список ID применимых продуктов"""
        if not self.applicable_products:
            return []
        return [int(p.strip()) for p in self.applicable_products.split(',') if p.strip()]
    
    def set_applicable_products_list(self, product_ids):
        """Установить список применимых продуктов"""
        self.applicable_products = ','.join(str(pid) for pid in product_ids)
    
    def is_active(self):
        """Проверка активности промоакции"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    def has_date_conflict(self):
        """Проверка на конфликт дат (окончание раньше начала)"""
        return self.end_date < self.start_date


class PromotionConflict(models.Model):
    """Модель для отслеживания конфликтов промоакций"""
    
    promotion1 = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name='conflicts_as_first'
    )
    promotion2 = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name='conflicts_as_second'
    )
    conflicting_products = models.TextField(
        'Конфликтующие продукты',
        help_text='ID продуктов через запятую'
    )
    overlap_start = models.DateTimeField('Начало пересечения')
    overlap_end = models.DateTimeField('Конец пересечения')
    resolved = models.BooleanField('Разрешён', default=False)
    resolution_method = models.CharField(
        'Метод разрешения',
        max_length=50,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField('Обнаружен', auto_now_add=True)
    
    class Meta:
        db_table = 'promotion_conflicts'
        verbose_name = 'Конфликт промоакций'
        verbose_name_plural = 'Конфликты промоакций'
        unique_together = ['promotion1', 'promotion2']
    
    def __str__(self):
        return f"Конфликт: {self.promotion1.name} ↔ {self.promotion2.name}"
    
    def get_conflicting_products_list(self):
        """Получить список конфликтующих продуктов"""
        if not self.conflicting_products:
            return []
        return [int(p.strip()) for p in self.conflicting_products.split(',') if p.strip()]
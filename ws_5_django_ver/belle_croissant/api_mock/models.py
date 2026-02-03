"""
Модели для mock API (имитация внешнего API)
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Customer(models.Model):
    """Модель клиента (mock API)"""
    
    MEMBERSHIP_STATUS_CHOICES = [
        ('Basic', 'Basic'),
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
    ]
    
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    membership_status = models.CharField(
        'Статус членства',
        max_length=20,
        choices=MEMBERSHIP_STATUS_CHOICES,
        default='Basic'
    )
    registration_date = models.DateField('Дата регистрации', auto_now_add=True)
    total_spending = models.DecimalField(
        'Общая сумма покупок',
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        db_table = 'mock_customers'
        verbose_name = 'Клиент (Mock)'
        verbose_name_plural = 'Клиенты (Mock)'
        ordering = ['-id']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Product(models.Model):
    """Модель продукта (mock API)"""
    
    CATEGORY_CHOICES = [
        ('croissant', 'Круассаны'),
        ('pastry', 'Выпечка'),
        ('bread', 'Хлеб'),
        ('cake', 'Торты'),
        ('drink', 'Напитки'),
    ]
    
    name = models.CharField('Название', max_length=200)
    category = models.CharField('Категория', max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(
        'Цена',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    description = models.TextField('Описание', blank=True)
    is_available = models.BooleanField('Доступен', default=True)
    
    class Meta:
        db_table = 'mock_products'
        verbose_name = 'Продукт (Mock)'
        verbose_name_plural = 'Продукты (Mock)'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.price}€)"


class Order(models.Model):
    """Модель заказа (mock API)"""
    
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('processing', 'Обрабатывается'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_date = models.DateTimeField('Дата заказа', auto_now_add=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(
        'Общая сумма',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    notes = models.TextField('Примечания', blank=True)
    
    class Meta:
        db_table = 'mock_orders'
        verbose_name = 'Заказ (Mock)'
        verbose_name_plural = 'Заказы (Mock)'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.customer.get_full_name()} ({self.total_amount}€)"


class OrderItem(models.Model):
    """Модель элемента заказа (mock API)"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        'Цена за единицу',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    subtotal = models.DecimalField(
        'Подытог',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        db_table = 'mock_order_items'
        verbose_name = 'Элемент заказа (Mock)'
        verbose_name_plural = 'Элементы заказов (Mock)'
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        """Автоматический расчёт подытога"""
        self.subtotal = Decimal(self.quantity) * self.unit_price
        super().save(*args, **kwargs)
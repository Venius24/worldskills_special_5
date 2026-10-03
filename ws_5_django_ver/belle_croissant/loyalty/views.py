"""
Views для управления программой лояльности
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import LoyaltyProgram, LoyaltyTransaction, RewardRedemption
from api_mock.models import Customer, Order
from promotions.models import Promotion


def loyalty_list(request):
    """Список клиентов с программой лояльности"""
    
    # Поиск
    search_query = request.GET.get('search', '')
    
    # Получаем всех клиентов
    customers = Customer.objects.all()
    
    if search_query:
        customers = customers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # Сортировка
    sort_by = request.GET.get('sort', '-id')
    valid_sorts = ['id', '-id', 'first_name', '-first_name', 'last_name', '-last_name', 
                   'email', '-email', 'membership_status', '-membership_status', 
                   'total_spending', '-total_spending']
    
    if sort_by in valid_sorts:
        customers = customers.order_by(sort_by)
    
    # Добавляем информацию о баллах лояльности
    customers_data = []
    for customer in customers:
        try:
            loyalty = LoyaltyProgram.objects.get(customer_id=customer.id)
            loyalty_points = loyalty.loyalty_points
        except LoyaltyProgram.DoesNotExist:
            loyalty_points = 0
        
        customers_data.append({
            'customer': customer,
            'loyalty_points': loyalty_points
        })
    
    # Пагинация
    try:
        per_page = min(max(int(request.GET.get('per_page', 10)), 1), 100)
    except ValueError:
        per_page = 10
    paginator = Paginator(customers_data, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
        'per_page': per_page,
    }
    
    return render(request, 'loyalty/list.html', context)


def loyalty_detail(request, customer_id):
    """Детальная информация о клиенте и его баллах"""
    
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Получаем или создаём программу лояльности
    loyalty, created = LoyaltyProgram.objects.get_or_create(
        customer_id=customer_id,
        defaults={
            'membership_status': customer.membership_status,
            'loyalty_points': 0
        }
    )
    
    # Получаем историю транзакций
    transactions = LoyaltyTransaction.objects.filter(
        loyalty_program=loyalty
    ).order_by('-created_at')[:20]
    
    # Получаем историю обменов наград
    redemptions = RewardRedemption.objects.filter(
        loyalty_program=loyalty
    ).order_by('-redeemed_at')[:10]
    
    context = {
        'customer': customer,
        'loyalty': loyalty,
        'transactions': transactions,
        'redemptions': redemptions,
        'can_redeem': loyalty.can_redeem_rewards(),
        'can_upgrade': loyalty.can_upgrade_membership(),
        'next_level': loyalty.get_next_membership_level(),
    }
    
    return render(request, 'loyalty/detail.html', context)


def loyalty_update_points(request, customer_id):
    """Обновление баллов лояльности вручную"""
    
    if request.method == 'POST':
        customer = get_object_or_404(Customer, id=customer_id)
        loyalty = get_object_or_404(LoyaltyProgram, customer_id=customer_id)
        
        try:
            new_points = int(request.POST.get('loyalty_points', 0))
            
            if new_points < 0:
                messages.error(request, 'Баллы не могут быть отрицательными!')
                return redirect('loyalty:detail', customer_id=customer_id)
            
            old_points = loyalty.loyalty_points
            difference = new_points - old_points
            
            loyalty.loyalty_points = new_points
            loyalty.save()
            
            # Записываем транзакцию
            LoyaltyTransaction.objects.create(
                loyalty_program=loyalty,
                transaction_type='adjustment',
                points=difference,
                description='Ручная корректировка баллов'
            )
            
            messages.success(request, f'Баллы обновлены: {old_points} → {new_points}')
            
        except ValueError:
            messages.error(request, 'Некорректное значение баллов!')
    
    return redirect('loyalty:detail', customer_id=customer_id)


def loyalty_recalculate_points(request, customer_id):
    """Пересчёт баллов на основе истории заказов"""
    
    customer = get_object_or_404(Customer, id=customer_id)
    loyalty = get_object_or_404(LoyaltyProgram, customer_id=customer_id)
    
    # Получаем все завершённые заказы клиента
    orders = Order.objects.filter(
        customer=customer,
        status='completed'
    ).order_by('order_date')
    
    # Получаем список активных промоакций за период
    promotion_dates = set()
    for promo in Promotion.objects.all():
        # Генерируем все даты между start_date и end_date
        current = promo.start_date.date()
        end = promo.end_date.date()
        while current <= end:
            promotion_dates.add(current)
            current += timedelta(days=1)
    
    # Расчёт баллов
    total_points = 0
    breakdown = []
    
    multiplier = loyalty.get_points_multiplier()
    
    for order in orders:
        order_date = order.order_date.date()
        
        # Базовые баллы за покупку
        base_points = int(order.total_amount / 10) * multiplier
        bonus_points = 0
        
        # Бонус за покупку в период промоакции
        if order_date in promotion_dates:
            bonus_points += 5
        
        # Бонус за годовщину
        if order_date.month == loyalty.registration_date.month and \
           order_date.day == loyalty.registration_date.day:
            bonus_points += 25
        
        order_total_points = base_points + bonus_points
        total_points += order_total_points
        
        breakdown.append({
            'order_id': order.id,
            'order_date': order.order_date.date().isoformat(),
            'amount': str(order.total_amount),
            'base_points': base_points,
            'bonus_points': bonus_points,
            'total_points': order_total_points,
            'is_promotion': order_date in promotion_dates,
            'is_anniversary': order_date.month == loyalty.registration_date.month and 
                            order_date.day == loyalty.registration_date.day
        })
    
    # Сохраняем расчёт в сессии для отображения
    request.session['points_breakdown'] = {
        'customer_id': customer_id,
        'total_points': total_points,
        'current_points': loyalty.loyalty_points,
        'breakdown': breakdown,
        'multiplier': multiplier,
    }
    
    return redirect('loyalty:confirm_recalculation', customer_id=customer_id)


def loyalty_confirm_recalculation(request, customer_id):
    """Подтверждение пересчёта баллов"""
    
    customer = get_object_or_404(Customer, id=customer_id)
    loyalty = get_object_or_404(LoyaltyProgram, customer_id=customer_id)
    
    breakdown_data = request.session.get('points_breakdown')
    
    if not breakdown_data or breakdown_data.get('customer_id') != customer_id:
        messages.error(request, 'Данные о пересчёте не найдены. Выполните пересчёт заново.')
        return redirect('loyalty:detail', customer_id=customer_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirm':
            old_points = loyalty.loyalty_points
            new_points = breakdown_data['total_points']
            
            loyalty.loyalty_points = new_points
            loyalty.last_points_calculation = timezone.now()
            loyalty.save()
            
            # Записываем транзакцию
            LoyaltyTransaction.objects.create(
                loyalty_program=loyalty,
                transaction_type='earn',
                points=new_points - old_points,
                description='Пересчёт баллов на основе истории заказов'
            )
            
            del request.session['points_breakdown']
            messages.success(request, f'Баллы пересчитаны: {old_points} → {new_points}')
            return redirect('loyalty:detail', customer_id=customer_id)
        
        elif action == 'cancel':
            del request.session['points_breakdown']
            messages.info(request, 'Пересчёт баллов отменён.')
            return redirect('loyalty:detail', customer_id=customer_id)
    
    context = {
        'customer': customer,
        'loyalty': loyalty,
        'breakdown': breakdown_data,
    }
    
    return render(request, 'loyalty/confirm_recalculation.html', context)


def loyalty_redeem_reward(request, customer_id):
    """Обмен баллов на награды"""
    
    customer = get_object_or_404(Customer, id=customer_id)
    loyalty = get_object_or_404(LoyaltyProgram, customer_id=customer_id)
    
    if not loyalty.can_redeem_rewards():
        messages.error(request, 'Недостаточно баллов для обмена на награды!')
        return redirect('loyalty:detail', customer_id=customer_id)
    
    if request.method == 'POST':
        reward_type = request.POST.get('reward_type')
        
        if reward_type == 'fixed_discount':
            # Создаём промоакцию со скидкой 5€
            promo = Promotion.objects.create(
                name=f'Награда клиента #{customer_id}: Скидка 5€',
                discount_type='fixed',
                discount_value=Decimal('5.00'),
                applicable_products=','.join(str(p.id) for p in Product.objects.all()),
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=30),
                priority=99
            )
            
            # Записываем обмен
            redemption = RewardRedemption.objects.create(
                loyalty_program=loyalty,
                reward_type='fixed_discount',
                points_spent=1000,
                promotion_id=promo.id
            )
            
        elif reward_type == 'percentage_discount':
            # Создаём промоакцию со скидкой 10%
            promo = Promotion.objects.create(
                name=f'Награда клиента #{customer_id}: Скидка 10%',
                discount_type='percentage',
                discount_value=Decimal('10.00'),
                applicable_products=','.join(str(p.id) for p in Product.objects.all()),
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=30),
                priority=99
            )
            
            redemption = RewardRedemption.objects.create(
                loyalty_program=loyalty,
                reward_type='percentage_discount',
                points_spent=1000,
                promotion_id=promo.id
            )
            
        elif reward_type == 'membership_upgrade':
            if not loyalty.can_upgrade_membership():
                messages.error(request, 'Невозможно повысить уровень членства!')
                return redirect('loyalty:detail', customer_id=customer_id)
            
            old_status = loyalty.membership_status
            new_status = loyalty.get_next_membership_level()
            
            loyalty.membership_status = new_status
            customer.membership_status = new_status
            customer.save()
            
            redemption = RewardRedemption.objects.create(
                loyalty_program=loyalty,
                reward_type='membership_upgrade',
                points_spent=1000
            )
            
            messages.success(request, f'Статус повышен: {old_status} → {new_status}')
        
        else:
            messages.error(request, 'Неверный тип награды!')
            return redirect('loyalty:detail', customer_id=customer_id)
        
        # Списываем баллы
        loyalty.loyalty_points -= 1000
        loyalty.save()
        
        # Записываем транзакцию
        LoyaltyTransaction.objects.create(
            loyalty_program=loyalty,
            transaction_type='redeem',
            points=-1000,
            description=f'Обмен на награду: {redemption.get_reward_type_display()}'
        )
        
        messages.success(request, 'Награда успешно обменяна! Списано 1000 баллов.')
        return redirect('loyalty:detail', customer_id=customer_id)
    
    context = {
        'customer': customer,
        'loyalty': loyalty,
    }
    
    return render(request, 'loyalty/redeem.html', context)


# Импорт Product для обмена наград
from api_mock.models import Product

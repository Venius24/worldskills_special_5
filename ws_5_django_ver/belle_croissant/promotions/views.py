"""
Views для управления промоакциями
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
import json

from .models import Promotion, PromotionConflict
from api_mock.models import Product


def promotion_list(request):
    """Список промоакций"""
    promotions = Promotion.objects.all().order_by('-priority', '-start_date')
    products = Product.objects.all()
    
    context = {
        'promotions': promotions,
        'products': products,
    }
    return render(request, 'promotions/list.html', context)


def promotion_create(request):
    """Создание новой промоакции"""
    if request.method == 'POST':
        try:
            # Получение данных из формы
            name = request.POST.get('name')
            discount_type = request.POST.get('discount_type')
            discount_value = request.POST.get('discount_value')
            applicable_products = request.POST.getlist('applicable_products')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            minimum_order_value = request.POST.get('minimum_order_value') or None
            priority = request.POST.get('priority', 1)
            
            # Создание промоакции
            promotion = Promotion.objects.create(
                name=name,
                discount_type=discount_type,
                discount_value=discount_value,
                applicable_products=','.join(applicable_products),
                start_date=datetime.fromisoformat(start_date),
                end_date=datetime.fromisoformat(end_date),
                minimum_order_value=minimum_order_value,
                priority=priority
            )
            
            # Проверка конфликтов
            conflicts = check_promotion_conflicts(promotion)
            
            if conflicts:
                # Сохраняем ID промоакции в сессии для мастера разрешения
                request.session['pending_promotion_id'] = promotion.id
                request.session['conflicts'] = conflicts
                return redirect('promotions:conflict_wizard')
            
            messages.success(request, f'Промоакция "{promotion.name}" успешно создана!')
            return redirect('promotions:list')
            
        except Exception as e:
            messages.error(request, f'Ошибка при создании промоакции: {str(e)}')
            return redirect('promotions:list')
    
    return redirect('promotions:list')


def promotion_update(request, pk):
    """Обновление промоакции"""
    promotion = get_object_or_404(Promotion, pk=pk)
    
    if request.method == 'POST':
        try:
            promotion.name = request.POST.get('name')
            promotion.discount_type = request.POST.get('discount_type')
            promotion.discount_value = request.POST.get('discount_value')
            applicable_products = request.POST.getlist('applicable_products')
            promotion.applicable_products = ','.join(applicable_products)
            promotion.start_date = datetime.fromisoformat(request.POST.get('start_date'))
            promotion.end_date = datetime.fromisoformat(request.POST.get('end_date'))
            promotion.minimum_order_value = request.POST.get('minimum_order_value') or None
            promotion.priority = request.POST.get('priority', 1)
            
            # Проверка конфликтов
            conflicts = check_promotion_conflicts(promotion, exclude_self=True)
            
            if conflicts:
                request.session['pending_promotion_id'] = promotion.id
                request.session['conflicts'] = conflicts
                return redirect('promotions:conflict_wizard')
            
            promotion.save()
            messages.success(request, f'Промоакция "{promotion.name}" успешно обновлена!')
            
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении промоакции: {str(e)}')
    
    return redirect('promotions:list')


def promotion_delete(request, pk):
    """Удаление промоакции"""
    promotion = get_object_or_404(Promotion, pk=pk)
    
    if request.method == 'POST':
        name = promotion.name
        promotion.delete()
        messages.success(request, f'Промоакция "{name}" успешно удалена!')
    
    return redirect('promotions:list')


def check_promotion_conflicts(promotion, exclude_self=False):
    """
    Проверка конфликтов промоакции с существующими
    Возвращает список конфликтов
    """
    conflicts = []
    
    # Получаем список применимых продуктов
    promotion_products = set(promotion.get_applicable_products_list())
    
    # Ищем другие промоакции с тем же приоритетом
    query = Promotion.objects.filter(priority=promotion.priority)
    
    if exclude_self and promotion.id:
        query = query.exclude(id=promotion.id)
    
    for other_promo in query:
        other_products = set(other_promo.get_applicable_products_list())
        
        # Находим общие продукты
        common_products = promotion_products & other_products
        
        if not common_products:
            continue
        
        # Проверяем пересечение дат
        overlap_start = max(promotion.start_date, other_promo.start_date)
        overlap_end = min(promotion.end_date, other_promo.end_date)
        
        if overlap_start <= overlap_end:
            conflicts.append({
                'promotion1_id': promotion.id,
                'promotion1_name': promotion.name,
                'promotion2_id': other_promo.id,
                'promotion2_name': other_promo.name,
                'common_products': list(common_products),
                'overlap_start': overlap_start.isoformat(),
                'overlap_end': overlap_end.isoformat(),
                'priority': promotion.priority
            })
    
    return conflicts


def conflict_wizard(request):
    """Мастер разрешения конфликтов"""
    
    # Получаем данные о конфликтах из сессии
    pending_promotion_id = request.session.get('pending_promotion_id')
    conflicts = request.session.get('conflicts', [])
    
    if not pending_promotion_id or not conflicts:
        messages.info(request, 'Нет активных конфликтов для разрешения.')
        return redirect('promotions:list')
    
    promotion = get_object_or_404(Promotion, pk=pending_promotion_id)
    products = Product.objects.all()
    
    # Получаем текущий шаг мастера
    step = request.session.get('wizard_step', 1)
    current_conflict_index = request.session.get('current_conflict_index', 0)
    
    if current_conflict_index >= len(conflicts):
        # Все конфликты разрешены
        del request.session['pending_promotion_id']
        del request.session['conflicts']
        del request.session['wizard_step']
        del request.session['current_conflict_index']
        messages.success(request, f'Все конфликты разрешены! Промоакция "{promotion.name}" сохранена.')
        return redirect('promotions:list')
    
    current_conflict = conflicts[current_conflict_index]
    
    context = {
        'promotion': promotion,
        'conflicts': conflicts,
        'current_conflict': current_conflict,
        'current_conflict_index': current_conflict_index,
        'step': step,
        'total_conflicts': len(conflicts),
        'products': products,
    }
    
    return render(request, 'promotions/conflict_wizard.html', context)


def wizard_next_step(request):
    """Переход к следующему шагу мастера"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'next_conflict':
            current_index = request.session.get('current_conflict_index', 0)
            request.session['current_conflict_index'] = current_index + 1
            request.session['wizard_step'] = 1
            
        elif action == 'change_priority':
            promotion_id = request.session.get('pending_promotion_id')
            new_priority = int(request.POST.get('new_priority'))
            
            promotion = Promotion.objects.get(pk=promotion_id)
            promotion.priority = new_priority
            promotion.save()
            
            # Пересчитываем конфликты
            conflicts = check_promotion_conflicts(promotion, exclude_self=True)
            request.session['conflicts'] = conflicts
            request.session['current_conflict_index'] = 0
            
            if not conflicts:
                del request.session['pending_promotion_id']
                del request.session['conflicts']
                messages.success(request, 'Приоритет изменён, конфликтов больше нет!')
                return redirect('promotions:list')
            
        elif action == 'adjust_dates':
            promotion_id = request.session.get('pending_promotion_id')
            new_start = request.POST.get('new_start_date')
            new_end = request.POST.get('new_end_date')
            
            promotion = Promotion.objects.get(pk=promotion_id)
            if new_start:
                promotion.start_date = datetime.fromisoformat(new_start)
            if new_end:
                promotion.end_date = datetime.fromisoformat(new_end)
            promotion.save()
            
            # Пересчитываем конфликты
            conflicts = check_promotion_conflicts(promotion, exclude_self=True)
            request.session['conflicts'] = conflicts
            request.session['current_conflict_index'] = 0
            
            if not conflicts:
                del request.session['pending_promotion_id']
                del request.session['conflicts']
                messages.success(request, 'Даты изменены, конфликтов больше нет!')
                return redirect('promotions:list')
            
        elif action == 'remove_products':
            promotion_id = request.session.get('pending_promotion_id')
            products_to_remove = request.POST.getlist('products_to_remove')
            
            promotion = Promotion.objects.get(pk=promotion_id)
            current_products = set(promotion.get_applicable_products_list())
            current_products -= set(int(p) for p in products_to_remove)
            promotion.set_applicable_products_list(list(current_products))
            promotion.save()
            
            # Пересчитываем конфликты
            conflicts = check_promotion_conflicts(promotion, exclude_self=True)
            request.session['conflicts'] = conflicts
            request.session['current_conflict_index'] = 0
            
            if not conflicts:
                del request.session['pending_promotion_id']
                del request.session['conflicts']
                messages.success(request, 'Продукты удалены, конфликтов больше нет!')
                return redirect('promotions:list')
        
        elif action == 'cancel':
            promotion_id = request.session.get('pending_promotion_id')
            promotion = Promotion.objects.get(pk=promotion_id)
            promotion.delete()
            
            del request.session['pending_promotion_id']
            del request.session['conflicts']
            messages.info(request, 'Создание промоакции отменено.')
            return redirect('promotions:list')
    
    return redirect('promotions:conflict_wizard')


def get_promotion_data(request, pk):
    """API для получения данных промоакции (AJAX)"""
    promotion = get_object_or_404(Promotion, pk=pk)
    
    data = {
        'id': promotion.id,
        'name': promotion.name,
        'discount_type': promotion.discount_type,
        'discount_value': float(promotion.discount_value),
        'applicable_products': promotion.get_applicable_products_list(),
        'start_date': promotion.start_date.isoformat(),
        'end_date': promotion.end_date.isoformat(),
        'minimum_order_value': float(promotion.minimum_order_value) if promotion.minimum_order_value else None,
        'priority': promotion.priority,
    }
    
    return JsonResponse(data)
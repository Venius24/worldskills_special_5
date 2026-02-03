"""
Mock API Views (имитация внешнего API)
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import Customer, Product, Order, OrderItem


@require_http_methods(["GET"])
def customers_list(request):
    """API: Список клиентов"""
    
    # Параметры пагинации
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 20))
    
    # Поиск
    search = request.GET.get('search', '')
    
    customers = Customer.objects.all()
    
    if search:
        customers = customers.filter(
            first_name__icontains=search
        ) | customers.filter(
            last_name__icontains=search
        ) | customers.filter(
            email__icontains=search
        )
    
    # Пагинация
    paginator = Paginator(customers, per_page)
    page_obj = paginator.get_page(page)
    
    data = {
        'count': paginator.count,
        'page': page,
        'per_page': per_page,
        'total_pages': paginator.num_pages,
        'results': [
            {
                'id': c.id,
                'first_name': c.first_name,
                'last_name': c.last_name,
                'email': c.email,
                'phone': c.phone,
                'membership_status': c.membership_status,
                'registration_date': c.registration_date.isoformat(),
                'total_spending': float(c.total_spending),
            }
            for c in page_obj
        ]
    }
    
    return JsonResponse(data)


@require_http_methods(["GET"])
def customer_detail(request, customer_id):
    """API: Детали клиента"""
    
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=404)
    
    data = {
        'id': customer.id,
        'first_name': customer.first_name,
        'last_name': customer.last_name,
        'email': customer.email,
        'phone': customer.phone,
        'membership_status': customer.membership_status,
        'registration_date': customer.registration_date.isoformat(),
        'total_spending': float(customer.total_spending),
    }
    
    return JsonResponse(data)


@require_http_methods(["GET"])
def products_list(request):
    """API: Список продуктов"""
    
    category = request.GET.get('category')
    
    products = Product.objects.filter(is_available=True)
    
    if category:
        products = products.filter(category=category)
    
    data = {
        'count': products.count(),
        'results': [
            {
                'id': p.id,
                'name': p.name,
                'category': p.category,
                'price': float(p.price),
                'description': p.description,
                'is_available': p.is_available,
            }
            for p in products
        ]
    }
    
    return JsonResponse(data)


@require_http_methods(["GET"])
def product_detail(request, product_id):
    """API: Детали продукта"""
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    data = {
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'price': float(product.price),
        'description': product.description,
        'is_available': product.is_available,
    }
    
    return JsonResponse(data)


@require_http_methods(["GET"])
def orders_list(request):
    """API: Список заказов"""
    
    customer_id = request.GET.get('customer_id')
    status = request.GET.get('status')
    
    orders = Order.objects.all()
    
    if customer_id:
        orders = orders.filter(customer_id=customer_id)
    
    if status:
        orders = orders.filter(status=status)
    
    # Пагинация
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 50))
    
    paginator = Paginator(orders, per_page)
    page_obj = paginator.get_page(page)
    
    data = {
        'count': paginator.count,
        'page': page,
        'per_page': per_page,
        'total_pages': paginator.num_pages,
        'results': [
            {
                'id': o.id,
                'customer_id': o.customer_id,
                'order_date': o.order_date.isoformat(),
                'status': o.status,
                'total_amount': float(o.total_amount),
                'notes': o.notes,
            }
            for o in page_obj
        ]
    }
    
    return JsonResponse(data)


@require_http_methods(["GET"])
def order_detail(request, order_id):
    """API: Детали заказа с элементами"""
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
    items = OrderItem.objects.filter(order=order)
    
    data = {
        'id': order.id,
        'customer': {
            'id': order.customer.id,
            'first_name': order.customer.first_name,
            'last_name': order.customer.last_name,
            'email': order.customer.email,
        },
        'order_date': order.order_date.isoformat(),
        'status': order.status,
        'total_amount': float(order.total_amount),
        'notes': order.notes,
        'items': [
            {
                'product_id': item.product_id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'subtotal': float(item.subtotal),
            }
            for item in items
        ]
    }
    
    return JsonResponse(data)


@require_http_methods(["GET"])
def customer_orders(request, customer_id):
    """API: Заказы конкретного клиента"""
    
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=404)
    
    orders = Order.objects.filter(customer=customer).order_by('-order_date')
    
    data = {
        'customer_id': customer_id,
        'count': orders.count(),
        'orders': [
            {
                'id': o.id,
                'order_date': o.order_date.isoformat(),
                'status': o.status,
                'total_amount': float(o.total_amount),
            }
            for o in orders
        ]
    }
    
    return JsonResponse(data)
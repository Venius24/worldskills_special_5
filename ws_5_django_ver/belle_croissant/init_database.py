"""
Database initialization script for Belle Croissant Lyonnais
Run: python manage.py shell < init_database.py
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

from api_mock.models import Customer, Product, Order, OrderItem
from promotions.models import Promotion
from loyalty.models import LoyaltyProgram


def clear_database():
    print("Clearing database...")
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Promotion.objects.all().delete()
    LoyaltyProgram.objects.all().delete()
    print("OK: Database cleared")


def create_products():
    print("\nCreating products...")
    products_data = [
        ('Croissant Classic', 'croissant', 2.50),
        ('Croissant Chocolate', 'croissant', 3.00),
        ('Croissant Almond', 'croissant', 3.50),
        ('Croissant Ham & Cheese', 'croissant', 4.50),
        ('Pain au chocolat', 'pastry', 2.80),
        ('Eclair', 'pastry', 4.00),
        ('Macaron 6pcs', 'pastry', 12.00),
        ('Fruit Tart', 'pastry', 5.50),
        ('Traditional Baguette', 'bread', 1.80),
        ('Sourdough Bread', 'bread', 4.20),
        ('Rolls 4pcs', 'bread', 3.50),
        ('Opera Cake', 'cake', 28.00),
        ('Cheesecake', 'cake', 25.00),
        ('Fruit Cake', 'cake', 30.00),
        ('Espresso', 'drink', 2.00),
        ('Cappuccino', 'drink', 3.50),
        ('Latte', 'drink', 4.00),
        ('Tea', 'drink', 2.50),
        ('Fresh Juice', 'drink', 5.00),
    ]
    
    products = []
    for name, category, price in products_data:
        product = Product.objects.create(
            name=name,
            category=category,
            price=Decimal(str(price)),
            is_available=True
        )
        products.append(product)
    
    print(f"OK: Created {len(products)} products")
    return products


def create_customers():
    print("\nCreating customers...")
    
    first_names = ['Anna', 'Maria', 'Elena', 'Olga', 'Natalia', 'Tatiana', 'Irina', 'Svetlana',
                   'Alexander', 'Dmitry', 'Sergey', 'Andrey', 'Michael', 'Vladimir', 'Igor', 'Pavel']
    last_names = ['Ivanova', 'Petrova', 'Sidorova', 'Kuznetsova', 'Smirnova', 'Popova', 'Vasileva',
                  'Ivanov', 'Petrov', 'Sidorov', 'Kuznetsov', 'Smirnov', 'Popov', 'Vasilev']
    
    customers = []
    for i in range(1000):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
        
        rand = random.random()
        if rand < 0.7:
            status = 'Basic'
        elif rand < 0.9:
            status = 'Silver'
        else:
            status = 'Gold'
        
        days_ago = random.randint(0, 1095)
        reg_date = (timezone.now() - timedelta(days=days_ago)).date()
        
        customer = Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            membership_status=status,
            total_spending=Decimal('0.00')
        )
        customer.registration_date = reg_date
        customer.save()
        
        customers.append(customer)
    
    print(f"OK: Created {len(customers)} customers")
    return customers


def create_orders(customers, products):
    print("\nCreating orders...")
    
    orders = []
    for customer in customers:
        num_orders = random.randint(0, 20)
        
        for _ in range(num_orders):
            days_since_reg = (timezone.now().date() - customer.registration_date).days
            if days_since_reg > 0:
                order_days_ago = random.randint(0, days_since_reg)
                order_date = timezone.now() - timedelta(days=order_days_ago)
            else:
                order_date = timezone.now()
            
            order = Order.objects.create(
                customer=customer,
                status='completed',
                total_amount=Decimal('0.00')
            )
            order.order_date = order_date
            order.save()
            
            num_items = random.randint(1, 5)
            total = Decimal('0.00')
            
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price
                )
                total += product.price * quantity
            
            order.total_amount = total
            order.save()
            
            customer.total_spending += total
            customer.save()
            
            orders.append(order)
    
    print(f"OK: Created {len(orders)} orders")
    return orders


def create_promotions(products):
    print("\nCreating promotions...")
    
    now = timezone.now()
    
    promotions_data = [
        {
            'name': 'Discount 20% on all croissants',
            'discount_type': 'percentage',
            'discount_value': 20,
            'products': [p.id for p in products if p.category == 'croissant'],
            'start_date': now - timedelta(days=10),
            'end_date': now + timedelta(days=20),
            'priority': 5
        },
        {
            'name': 'Fixed 5 EUR discount on cakes',
            'discount_type': 'fixed',
            'discount_value': 5,
            'products': [p.id for p in products if p.category == 'cake'],
            'start_date': now - timedelta(days=5),
            'end_date': now + timedelta(days=15),
            'priority': 3
        },
        {
            'name': 'Morning deal: 15% on pastries',
            'discount_type': 'percentage',
            'discount_value': 15,
            'products': [p.id for p in products if p.category == 'pastry'],
            'start_date': now,
            'end_date': now + timedelta(days=30),
            'priority': 4,
            'minimum_order_value': 10
        },
        {
            'name': '10% on bread with 20 EUR purchase',
            'discount_type': 'percentage',
            'discount_value': 10,
            'products': [p.id for p in products if p.category == 'bread'],
            'start_date': now - timedelta(days=15),
            'end_date': now + timedelta(days=45),
            'priority': 2,
            'minimum_order_value': 20
        },
        {
            'name': 'Combo deal: croissant + coffee',
            'discount_type': 'fixed',
            'discount_value': 2,
            'products': [p.id for p in products if p.category in ['croissant', 'drink']],
            'start_date': now - timedelta(days=20),
            'end_date': now + timedelta(days=10),
            'priority': 5
        },
        {
            'name': 'Weekend sale: 25% on everything',
            'discount_type': 'percentage',
            'discount_value': 25,
            'products': [p.id for p in products],
            'start_date': now + timedelta(days=5),
            'end_date': now + timedelta(days=7),
            'priority': 10
        },
        {
            'name': 'Special: macarons',
            'discount_type': 'percentage',
            'discount_value': 30,
            'products': [p.id for p in products if 'Macaron' in p.name],
            'start_date': now - timedelta(days=3),
            'end_date': now + timedelta(days=25),
            'priority': 7
        },
        {
            'name': 'Happy hours: drinks -20%',
            'discount_type': 'percentage',
            'discount_value': 20,
            'products': [p.id for p in products if p.category == 'drink'],
            'start_date': now + timedelta(days=1),
            'end_date': now + timedelta(days=14),
            'priority': 6
        },
        {
            'name': 'ERROR: Invalid dates',
            'discount_type': 'percentage',
            'discount_value': 50,
            'products': [products[0].id],
            'start_date': now + timedelta(days=30),
            'end_date': now - timedelta(days=10),
            'priority': 1
        },
        {
            'name': 'Conflict promo: croissants -15%',
            'discount_type': 'percentage',
            'discount_value': 15,
            'products': [p.id for p in products if p.category == 'croissant'],
            'start_date': now - timedelta(days=5),
            'end_date': now + timedelta(days=15),
            'priority': 5
        },
    ]
    
    promotions = []
    for promo_data in promotions_data:
        promo = Promotion.objects.create(
            name=promo_data['name'],
            discount_type=promo_data['discount_type'],
            discount_value=Decimal(str(promo_data['discount_value'])),
            applicable_products=','.join(str(pid) for pid in promo_data['products']),
            start_date=promo_data['start_date'],
            end_date=promo_data['end_date'],
            priority=promo_data['priority'],
            minimum_order_value=promo_data.get('minimum_order_value')
        )
        promotions.append(promo)
    
    print(f"OK: Created {len(promotions)} promotions")
    return promotions


def create_loyalty_programs(customers):
    print("\nCreating loyalty programs...")
    
    loyalty_programs = []
    
    for customer in customers:
        loyalty = LoyaltyProgram.objects.create(
            customer_id=customer.id,
            loyalty_points=0,
            membership_status=customer.membership_status
        )
        loyalty.registration_date = customer.registration_date
        loyalty.save()
        loyalty_programs.append(loyalty)
    
    active_customers = random.sample(loyalty_programs, 250)
    
    for loyalty in active_customers:
        points = random.randint(50, 1500)
        loyalty.loyalty_points = points
        loyalty.save()
    
    print(f"OK: Created {len(loyalty_programs)} loyalty programs")
    print(f"OK: 250 customers received active points")
    return loyalty_programs


def main():
    print("="*60)
    print("BELLE CROISSANT LYONNAIS - DATABASE INITIALIZATION")
    print("="*60)
    
    clear_database()
    
    products = create_products()
    customers = create_customers()
    orders = create_orders(customers, products)
    promotions = create_promotions(products)
    loyalty_programs = create_loyalty_programs(customers)
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    print(f"Products:          {len(products)}")
    print(f"Customers:         {len(customers)}")
    print(f"Orders:            {len(orders)}")
    print(f"Promotions:        {len(promotions)}")
    print(f"Loyalty programs:  {len(loyalty_programs)}")
    print("="*60)
    print("OK: Initialization completed successfully!")
    print("="*60)


if __name__ == '__main__':
    main()
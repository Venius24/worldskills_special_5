"""
Django management command for database initialization
Usage: python manage.py init_db
"""
import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone

from api_mock.models import Customer, Product, Order, OrderItem
from promotions.models import Promotion
from loyalty.models import LoyaltyProgram


class Command(BaseCommand):
    help = 'Initialize database with test data for Belle Croissant Lyonnais'

    def handle(self, *args, **options):
        self.stdout.write("="*60)
        self.stdout.write("BELLE CROISSANT LYONNAIS - DATABASE INITIALIZATION")
        self.stdout.write("="*60)
        
        self.clear_database()
        products = self.create_products()
        customers = self.create_customers()
        orders = self.create_orders(customers, products)
        promotions = self.create_promotions(products)
        loyalty_programs = self.create_loyalty_programs(customers)
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("SUMMARY:")
        self.stdout.write("="*60)
        self.stdout.write(f"Products:          {len(products)}")
        self.stdout.write(f"Customers:         {len(customers)}")
        self.stdout.write(f"Orders:            {len(orders)}")
        self.stdout.write(f"Promotions:        {len(promotions)}")
        self.stdout.write(f"Loyalty programs:  {len(loyalty_programs)}")
        self.stdout.write("="*60)
        self.stdout.write(self.style.SUCCESS("Initialization completed successfully!"))
        self.stdout.write("="*60)

    def clear_database(self):
        self.stdout.write("\nClearing database...")
        Order.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()
        Promotion.objects.all().delete()
        LoyaltyProgram.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("OK: Database cleared"))

    def create_products(self):
        self.stdout.write("\nCreating products...")
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
        
        self.stdout.write(self.style.SUCCESS(f"OK: Created {len(products)} products"))
        return products

    def create_customers(self):
        self.stdout.write("\nCreating customers...")
        
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
            
            if (i + 1) % 100 == 0:
                self.stdout.write(f"  Progress: {i + 1}/1000 customers")
        
        self.stdout.write(self.style.SUCCESS(f"OK: Created {len(customers)} customers"))
        return customers

    def create_orders(self, customers, products):
        self.stdout.write("\nCreating orders...")
        
        orders = []
        for idx, customer in enumerate(customers):
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
            
            if (idx + 1) % 100 == 0:
                self.stdout.write(f"  Progress: {idx + 1}/1000 customers processed")
        
        self.stdout.write(self.style.SUCCESS(f"OK: Created {len(orders)} orders"))
        return orders

    def create_promotions(self, products):
        self.stdout.write("\nCreating promotions...")
        
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
        
        self.stdout.write(self.style.SUCCESS(f"OK: Created {len(promotions)} promotions"))
        return promotions

    def create_loyalty_programs(self, customers):
        self.stdout.write("\nCreating loyalty programs...")
        
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
        
        self.stdout.write(self.style.SUCCESS(f"OK: Created {len(loyalty_programs)} loyalty programs"))
        self.stdout.write(self.style.SUCCESS("OK: 250 customers received active points"))
        return loyalty_programs
from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from api_mock.models import Customer, Order
from .models import LoyaltyProgram


class LoyaltyViewsTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='Test', last_name='Customer', email='test@example.com'
        )
        self.loyalty = LoyaltyProgram.objects.create(customer_id=self.customer.id)

    def test_recalculation_can_be_saved_in_json_session(self):
        order = Order.objects.create(
            customer=self.customer, status='completed', total_amount=Decimal('25.00')
        )
        Order.objects.filter(pk=order.pk).update(order_date=timezone.now() - timedelta(days=2))
        response = self.client.get(f'/loyalty/customer/{self.customer.id}/recalculate/')
        self.assertEqual(response.status_code, 302)
        breakdown = self.client.session['points_breakdown']
        self.assertEqual(breakdown['total_points'], 20)
        self.assertEqual(breakdown['breakdown'][0]['amount'], '25.00')
        self.assertEqual(
            self.client.get(f'/loyalty/customer/{self.customer.id}/confirm-recalculation/').status_code,
            200,
        )

    def test_invalid_page_size_uses_default(self):
        response = self.client.get('/loyalty/?per_page=invalid')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['per_page'], 10)

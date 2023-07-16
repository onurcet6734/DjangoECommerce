from django.test import TestCase
from django.contrib.auth.models import User
from store.models import Category, Customer, Product, Order, Address, Payment


class ModelsTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.customer = Customer.objects.create(user=self.user, name='Test Customer', email='test@example.com')
        self.product = Product.objects.create(title='Test Product', price=10, description='Test Description', category=self.category)
        self.order = Order.objects.create(customer=self.customer, product=self.product, quantity=2, total_price=20)
        self.address = Address.objects.create(customer=self.customer, order=self.order, address_line1='Address Line 1', city='City', state='State', postal_code='12345')
        self.payment = Payment.objects.create(order=self.order, payment_method='Test Payment', transaction_id='123456789', amount=20)

    def test_category_model(self):
        self.assertEqual(str(self.category), 'Test Category')

    def test_customer_model(self):
        self.assertEqual(str(self.customer), 'Test Customer')

    def test_product_model(self):
        self.assertEqual(str(self.product), 'Test Product')

    def test_order_model(self):
        self.assertEqual(str(self.order), f"Order #{self.order.pk}")

    def test_address_model(self):
        self.assertEqual(str(self.address), 'Address Line 1, City, State')

    def test_payment_model(self):
        self.assertEqual(str(self.payment), f"Payment for Order #{self.order.pk}")


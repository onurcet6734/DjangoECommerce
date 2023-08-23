from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product, Order
import json

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "ali_coban"
        self.password = "1234_?=)"
        self.user = User.objects.create_user(username= self.username, password=self.password)
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(category=self.category, title='Test Product', price=10)

    def test_index_view(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_handled_login_view(self):
        response = self.client.post(reverse('handled_login'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)  
        self.assertRedirects(response, reverse('index'))

    def test_cart_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')

    def test_add_to_cart_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'Item was added to cart')

    def test_delete_order_view(self):
        self.client.login(username='testuser', password='testpassword')
        order = Order.objects.create(customer=self.user.customer, product=self.product, quantity=2, total_price=20)
        response = self.client.post(reverse('delete_order', args=[order.id]))
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertRedirects(response, reverse('cart'))

    def test_product_detail_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail.html')

    def test_checkout_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')  


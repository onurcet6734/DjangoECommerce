from django.test import TestCase
from django.urls import reverse, resolve
from store.views import (
    index, product_detail, cart, add_to_cart, delete_order,
    checkout, handledLogin, payment_checkout
)

class UrlsTest(TestCase):
    def test_index_url(self):
        url = reverse('index')
        self.assertEqual(resolve(url).func, index)

    def test_cart_url(self):
        url = reverse('cart')
        self.assertEqual(resolve(url).func, cart)

    def test_checkout_url(self):
        url = reverse('checkout')
        self.assertEqual(resolve(url).func, checkout)

    def test_handledLogin_url(self):
        url = reverse('handledLogin')
        self.assertEqual(resolve(url).func, handledLogin)

    def test_payment_checkout_url(self):
        url = reverse('payment_checkout')
        self.assertEqual(resolve(url).func, payment_checkout)


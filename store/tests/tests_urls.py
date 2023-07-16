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

    # def test_product_detail_url(self):
    #     url = reverse('detail', args=[1])  # Burada 1 yerine mevcut bir ürün ID'si kullanabilirsiniz
    #     self.assertEqual(resolve(url).func, product_detail)    

    # def test_add_to_cart_url(self):
    #     url = reverse('add_to_cart', args=[1])  # Burada 1 yerine mevcut bir ürün ID'si kullanabilirsiniz
    #     self.assertEqual(resolve(url).func, add_to_cart)

    # def test_delete_order_url(self):
    #     url = reverse('delete_order', args=[1])  # Burada 1 yerine mevcut bir sipariş ID'si kullanabilirsiniz
    #     self.assertEqual(resolve(url).func, delete_order)

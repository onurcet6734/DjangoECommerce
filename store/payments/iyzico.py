import iyzipay
from django.conf import settings


class IyzicoPayment:

    def __init__(self):

        self.options = {
            'api_key': settings.IYZICO_API_KEY,
            'secret_key': settings.IYZICO_SECRET_KEY,
            'base_url': settings.IYZICO_BASE_URL
        }


    def create_checkout_form(self, request, orders, customer):

        total_price = sum([order.total_price for order in orders])

        basket_items = []

        for order in orders:

            basket_items.append({
                'id': str(order.id),
                'name': order.product.title,
                'category1': 'Product',
                'itemType': 'PHYSICAL',
                'price': str(order.total_price)
            })

        request_data = {
            'locale': 'tr',
            'conversationId': '123456',
            'price': str(total_price),
            'paidPrice': str(total_price),
            'currency': 'TRY',
            'basketId': 'B67832',
            'paymentGroup': 'PRODUCT',
            'callbackUrl': 'http://localhost:8000/iyzico/callback/',
            'buyer': {
                'id': str(customer.id),
                'name': customer.user.first_name,
                'surname': customer.user.last_name,
                'email': customer.user.email,
                'identityNumber': '11111111111',
                'registrationAddress': 'adres',
                'city': 'Istanbul',
                'country': 'Turkey',
                'zipCode': '34732'
            },
            'shippingAddress': {
                'contactName': customer.user.get_full_name(),
                'city': 'Istanbul',
                'country': 'Turkey',
                'address': 'adres',
                'zipCode': '34732'
            },
            'billingAddress': {
                'contactName': customer.user.get_full_name(),
                'city': 'Istanbul',
                'country': 'Turkey',
                'address': 'adres',
                'zipCode': '34732'
            },
            'basketItems': basket_items
        }

        checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(
            request_data,
            self.options
        )

        response = checkout_form_initialize.read().decode("utf-8")

        import json
        response_json = json.loads(response)

        return response_json["paymentPageUrl"]
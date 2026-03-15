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
        """
        IyziCo ödeme sayfasını oluşturur ve paymentPageUrl döner.
        """
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

        # callbackUrl içine customer.id ekleniyor, böylece POST callback'te user bilgisi alınabilir
        callback_url = f'http://localhost:8000/success/?payment_type=iyzico&conversationId={customer.id}'

        request_data = {
            'locale': 'tr',
            'conversationId': str(customer.id),  # IyziCo için gerekli ama callback'te gelmez, sadece referans
            'price': str(total_price),
            'paidPrice': str(total_price),
            'currency': 'TRY',
            'basketId': 'B67832',
            'paymentGroup': 'PRODUCT',
            'callbackUrl': callback_url,
            'buyer': {
                'id': str(customer.id),
                'name': customer.user.first_name,
                'surname': customer.user.last_name,
                'email': customer.user.email,
                'identityNumber': '11111111111',
                'registrationAddress': 'adres',
                'city': request.POST.get("city"),
                'country': 'Turkey',
                'zipCode': request.POST.get("postal_code")
            },
            'shippingAddress': {
                'contactName': customer.user.get_full_name(),
                'city': request.POST.get("city"),
                'country': 'Turkey',
                'address': 'adres',
                'zipCode': request.POST.get("postal_code")
            },
            'billingAddress': {
                'contactName': customer.user.get_full_name(),
                'city': request.POST.get("city"),
                'country': 'Turkey',
                'address': 'adres',
                'zipCode': request.POST.get("postal_code")
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
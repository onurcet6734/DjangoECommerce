import stripe
from django.conf import settings
from store.models import Order


class StripePayment:

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY


    def create_checkout_session(self, orders, request):

        line_items = []
        order_ids = []

        for order in orders:

            order_ids.append(str(order.id))

            line_items.append({
                "price_data": {
                    "currency": "try",
                    "product_data": {
                        "name": order.product.title
                    },
                    "unit_amount": int(order.product.price * 100),
                },
                "quantity": order.quantity,
            })

        checkout_session = stripe.checkout.Session.create(

            payment_method_types=["card"],

            line_items=line_items,

            mode="payment",

            success_url="http://localhost:8000/success/?session_id={CHECKOUT_SESSION_ID}",

            cancel_url="http://localhost:8000/cart/",

            metadata={
                "order_ids": ",".join(order_ids)
            }

        )

        return checkout_session


    def retrieve_session(self, session_id):

        return stripe.checkout.Session.retrieve(session_id)


    def handle_webhook_event(self, event):

        if event["type"] == "checkout.session.completed":

            session = event["data"]["object"]

            metadata = session.get("metadata", {})

            order_ids = metadata.get("order_ids", "")

            if not order_ids:
                return

            order_ids = [int(i) for i in order_ids.split(",")]

            orders = Order.objects.filter(
                id__in=order_ids,
                is_completed=False
            )

            for order in orders:

                product = order.product

                product.stock -= order.quantity
                product.save()

                order.is_completed = True
                order.save()
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse ,HttpResponse
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from .models import Product, Order, Customer, Address, Comment
from .utils import set_customer_cookie, get_customer_from_cookie
from store.api.serializers import ProductSerializer, OrderSerializer, CustomerSerializer
from store.models import CommentForm

class IndexView(View):


    def get(self, request):

        products = Product.objects.select_related('category').all()

        category_id = request.GET.get('category_id')
        if category_id:
            products = products.filter(category_id=category_id)

        search_query = request.GET.get('q')
        if search_query:
            products = products.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        total_item_count = 0

        if request.user.is_authenticated:
            try:
                customer = Customer.objects.get(user=request.user)
                total_item_count = Order.objects.filter(customer=customer).count()
            except Customer.DoesNotExist:
                pass

        context = {
            'products': products,
            'total_item_count': total_item_count,
            'search_query': search_query
        }

        return render(request, "index.html", context)


class HandledLoginView(APIView):


    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            try:
                customer = Customer.objects.get(user=user)
                customer.update_name_from_user()

                response = redirect('index')
                set_customer_cookie(response, customer)

                return response

            except Customer.DoesNotExist:
                return redirect('index')

        return render(
            request,
            'login.html',
            {'message': 'Geçersiz kullanıcı adı veya şifre!'}
        )


class CartView(APIView):


    @method_decorator(login_required)
    def get(self, request):

        orders = Order.objects.select_related(
            'customer',
            'product'
        ).filter(customer__user=request.user)

        total_price_sum = orders.aggregate(
            Sum('total_price')
        )['total_price__sum']

        total_item_count = orders.count()

        cargo_price = 20

        if total_price_sum and total_price_sum > 5000:
            cargo_price = 0

        order_serializer = OrderSerializer(
            orders,
            many=True,
            context={'request': request}
        )

        context = {
            'orders': order_serializer.data,
            'total_price_sum': total_price_sum,
            'total_item_count': total_item_count,
            'cargo_price': cargo_price
        }

        return render(request, "cart.html", context)


class AddToCartView(APIView):


    def post(self, request, product_id):

        product = get_object_or_404(Product, pk=product_id)

        quantity = int(request.POST.get('quantity', 1))

        if request.user.is_authenticated:

            try:
                customer = Customer.objects.get(user=request.user)

                order = Order.objects.create(
                    customer=customer,
                    product=product,
                    quantity=quantity,
                    total_price=product.price * quantity
                )

                product_serializer = ProductSerializer(
                    product,
                    context={'request': request}
                )

                customer_serializer = CustomerSerializer(customer)

                return JsonResponse({
                    'message': 'Item added to cart',
                    'product': product_serializer.data,
                    'customer': customer_serializer.data
                })

            except Customer.DoesNotExist:
                return JsonResponse({'message': 'Customer not found'})

        return JsonResponse({'message': 'Unauthorized user'})


class DeleteOrderView(View):

    @method_decorator(login_required)
    def post(self, request, order_id):

        order = get_object_or_404(
            Order,
            id=order_id,
            customer__user=request.user
        )

        order.delete()

        return redirect('cart')


class ProductDetailView(View):


    def get(self, request, product_id):

        product = get_object_or_404(Product, id=product_id)

        customer, created = Customer.objects.get_or_create(user=request.user)

        total_item_count = Order.objects.filter(customer=customer).count()

        comments = Comment.objects.select_related(
            'customer',
            'product'
        ).filter(product=product_id)

        return render(
            request,
            'detail.html',
            {
                'comments': comments,
                'product': product,
                'total_item_count': total_item_count
            }
        )


    @method_decorator(login_required)
    def post(self, request, product_id):

        product = get_object_or_404(Product, id=product_id)

        customer, created = Customer.objects.get_or_create(user=request.user)

        quantity = int(request.POST.get('quantity', 1))

        try:

            order = Order.objects.get(
                customer=customer,
                product=product
            )

            order.quantity += quantity
            order.total_price = product.price * order.quantity
            order.save()

        except Order.DoesNotExist:

            Order.objects.create(
                customer=customer,
                product=product,
                quantity=quantity,
                total_price=product.price * quantity
            )

        return redirect('cart')


class AddCommentView(View):


    @method_decorator(login_required)
    def post(self, request, product_id):

        url = request.META.get("HTTP_REFERER")

        customer = Customer.objects.get(user=request.user)

        product = get_object_or_404(Product, id=product_id)

        check_completed = Order.objects.filter(
            customer=customer,
            is_completed=True
        ).exists()

        if check_completed:

            form = CommentForm(request.POST)

            if form.is_valid():

                Comment.objects.create(
                    customer=customer,
                    product=product,
                    comment=form.cleaned_data['comment'],
                    rate=form.cleaned_data['rate']
                )

                return redirect(url)

        return redirect("index")


class CheckoutView(APIView):


    @method_decorator(login_required)
    def get(self, request):

        customer = get_object_or_404(Customer, user=request.user)

        orders = Order.objects.filter(customer=customer)

        if not orders.exists():
            return redirect('index')

        total_price_sum = orders.aggregate(
            Sum('total_price')
        )['total_price__sum']

        total_item_count = orders.count()

        context = {
            'total_price_sum': total_price_sum,
            'total_item_count': total_item_count
        }

        return render(request, 'address_form.html', context)


class PaymentCheckoutView(View):

    @method_decorator(login_required)
    def post(self, request):
        import ipdb; ipdb.set_trace()
        payment_method = request.POST.get("payment_method")

        address_line1 = request.POST.get("address_line1")
        address_line2 = request.POST.get("address_line2")
        city = request.POST.get("city")
        state = request.POST.get("state")
        postal_code = request.POST.get("postal_code")

        customer = get_object_or_404(Customer, user=request.user)

        orders = Order.objects.filter(
            customer=customer,
            is_completed=False
        ).select_related("product")

        if not orders.exists():
            return redirect("cart")

        # adresi kaydet
        for order in orders:
            Address.objects.create(
                order=order,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                postal_code=postal_code
            )

        if payment_method == "stripe":

            from .payments.stripe import StripePayment 
            stripe_payment = StripePayment()
            checkout_session = stripe_payment.create_checkout_session(
                orders=orders,
                request=request
            )

            return redirect(checkout_session.url, code=303)


        elif payment_method == "iyzico":

            from .payments.iyzico import IyzicoPayment
            iyzico_payment = IyzicoPayment()
            payment_url = iyzico_payment.create_checkout_form(
                request=request,
                orders=orders,
                customer=customer
            )

            return redirect(payment_url)

        return redirect("cart")
    # @method_decorator(login_required)
    # def post(self, request):

    #     stripe.api_key = settings.STRIPE_SECRET_KEY

    #     customer = get_object_or_404(Customer, user=request.user)

    #     orders = Order.objects.filter(
    #         customer=customer,
    #         is_completed=False
    #     ).prefetch_related("product")

    #     if not orders.exists():
    #         return redirect("cart")

    #     line_items = []

    #     for order in orders:
    #         line_items.append({
    #             "price_data": {
    #                 "currency": "try",
    #                 "product_data": {
    #                     "name": order.product.title
    #                 },
    #                 "unit_amount": int(order.product.price * 100),
    #             },
    #             "quantity": order.quantity,
    #         })

    #     checkout_session = stripe.checkout.Session.create(
    #         payment_method_types=["card"],
    #         line_items=line_items,
    #         mode="payment",
    #         success_url="http://localhost:8000/success/",
    #         cancel_url="http://localhost:8000/",
    #     )

    #     return redirect(checkout_session.url, code=303)


class SuccessView(View): 


    def get(self, request):

        session_id = request.GET.get("session_id")

        if not session_id:
            return render(request, "success.html")

        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == "paid":

            addresses = Address.objects.select_related(
                "order",
                "order__product"
            )

            for address in addresses:

                product = address.order.product

                product.stock -= address.order.quantity
                product.save()

                Order.objects.filter(
                    product=product
                ).update(is_completed=True)

        return render(request, "success.html")

# class StripeWebhookView(View):

    # @method_decorator(csrf_exempt)
    # def post(self, request):
    #     import ipdb;ipdb.set_trace()
    #     stripe.api_key = settings.STRIPE_SECRET_KEY
    #     payload = request.body
    #     sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    #     try:
    #         event = stripe.Webhook.construct_event(
    #             payload,
    #             sig_header,
    #             settings.STRIPE_WEBHOOK_SECRET
    #         )
    #     except Exception:
    #         return HttpResponse(status=400)

    #     if event["type"] == "checkout.session.completed":

    #         session = event["data"]["object"]
    #         metadata = session.get("metadata", {})
    #         order_ids = metadata.get("order_ids", "")
    #         customer_id = metadata.get("customer_id")

    #         if not order_ids:
    #             return HttpResponse(status=400)

    #         order_ids = [int(i) for i in order_ids.split(",")]
    #         orders = Order.objects.filter(id__in=order_ids, is_completed=False)

    #         for order in orders:
    #             product = order.product
    #             product.stock -= order.quantity
    #             product.save()

    #             order.is_completed = True
    #             order.save()

    #     return HttpResponse(status=200)
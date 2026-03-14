from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
import stripe

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

        customer = get_object_or_404(Customer, user=request.user)

        orders = Order.objects.filter(
            customer=customer
        ).prefetch_related("product")

        if not orders.exists():
            return redirect("cart")

        latest_order = orders.latest("created_at")

        Address.objects.create(
            customer=customer,
            order=latest_order,
            address_line1=request.POST.get("address_line1"),
            address_line2=request.POST.get("address_line2"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            postal_code=request.POST.get("postal_code")
        )

        line_items = []

        for order in orders:

            line_items.append({
                "price_data": {
                    "currency": "try",
                    "product_data": {
                        "name": order.product.title
                    },
                    "unit_amount": int(order.product.price * 100)
                },
                "quantity": order.quantity
            })

        stripe.api_key = settings.STRIPE_SECRET_KEY

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url="http://localhost:8000/success/?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:8000/cart/"
        )

        return redirect(session.url, code=303)


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


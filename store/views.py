from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views import View
import stripe
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Order, Customer, Address, Comment
from store.models import CommentForm
from .payments.iyzico import IyzicoPayment
from .payments.stripe import StripePayment 

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


class HandledLoginView(View):


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
                response.set_cookie('customer_id', customer)

                return response
            except Customer.DoesNotExist:
                return redirect('index')

        return render(
            request,
            'login.html',
            {'message': 'Geçersiz kullanıcı adı veya şifre!'}
        )


class CartView(View):


    @method_decorator(login_required)
    def get(self, request):
        print("CartView aktif edildi")
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

        context = {
            'orders': orders,
            'total_price_sum': total_price_sum,
            'total_item_count': total_item_count,
            'cargo_price': cargo_price
        }

        return render(request, "cart.html", context)


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


class CheckoutView(View):


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

        # Adresi kaydet
        for order in orders:
            Address.objects.create(
                order=order,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                postal_code=postal_code
            )

        # Ödeme yönlendirmeleri
        if payment_method == "stripe":
            stripe_payment = StripePayment()
            checkout_session = stripe_payment.create_checkout_session(
                orders=orders,
                request=request
            )
            return redirect(checkout_session.url, code=303)

        elif payment_method == "iyzico":
            iyzico_payment = IyzicoPayment()
            payment_url = iyzico_payment.create_checkout_form(
                request=request,
                orders=orders,
                customer=customer
            )
            return redirect(payment_url)

        return redirect("cart")


@method_decorator(csrf_exempt, name="dispatch")
class SuccessView(View):

    """
        After entering payment details in the Stripe and Iyzico interfaces, Iyzico sends the HTTP request using the POST method, 
        
        while Stripe uses the GET method. 

        Therefore, two methods (GET and POST) are required.

        Once the card information is entered, a “Complete Payment” button appears. That's the part I'm referring to.
    """

    def get(self, request):
        """
        Stripe success redirect
        """
        payment_type = request.GET.get("payment_type")

        if payment_type == "stripe":
            session_id = request.GET.get("session_id")
            if not session_id:
                return False
            session = stripe.checkout.Session.retrieve(session_id)
            payment_status = session.payment_status
            if payment_status == "paid":
                customer = get_object_or_404(Customer, user=request.user)
                self.complete_orders(customer=customer)

        return render(request, "success.html")

    def post(self, request):
        """
        IyziCo callback
        """
        payment_type = request.GET.get("payment_type")

        if payment_type == "iyzico":
            conversation_id = request.GET.get("conversationId")
            token = request.POST.get("token")

            if token and conversation_id:
                customer = get_object_or_404(Customer, id=conversation_id)
                self.complete_orders(customer=customer)

        return render(request, "success.html")

    def complete_orders(self, customer):
        """
        Customer üzerinden orderları tamamla ve stok düş
        """
        if not customer:
            return

        orders = Order.objects.filter(
            customer=customer,
            is_completed=False
        ).select_related("product")

        for order in orders:
            product = order.product
            product.stock -= order.quantity
            product.save()

            order.is_completed = True
            order.save()
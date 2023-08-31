from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Order, Customer, Address,Comment
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .utils import set_customer_cookie, get_customer_from_cookie, delete_customer_cookie
from store.api.serializers import ProductSerializer, OrderSerializer, CustomerSerializer, CategorySerializer
from django.conf import settings
import stripe
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from store.models import CommentForm


class IndexView(APIView):
    def get(self, request):
        products = Product.objects.select_related('category').all()

        category_id = request.GET.get('category_id')
        if category_id:
            products = products.filter(category_id=category_id)

        search_query = request.GET.get('q')
        if search_query:
            products = products.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

        total_item_count = 0
        customer_from_cookie = get_customer_from_cookie(request)
        
        custnumberid = Customer.objects.filter(name = customer_from_cookie).values_list('id', flat=True)
        print(custnumberid)
        adminOrders = Order.objects.filter(is_admin_product = True)
        if customer_from_cookie!=None:
            adminOrders.update(is_admin_product=False, customer = custnumberid)

        if request.user.is_authenticated:
            try:
                customer = Customer.objects.select_related('user').get(user=request.user)
                total_item_count = Order.objects.filter(customer=customer).count()
            except Customer.DoesNotExist:
                pass

        product_serializer = ProductSerializer(products, many=True, context={'request': request})

        context = {
            'products': product_serializer.data,
            'total_item_count': total_item_count,
            'search_query': search_query,
            'customer_from_cookie': customer_from_cookie,

        }
        # json_data = json.dumps(product_serializer.data)
        # print(json_data)
        return render(request, "index.html", context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class HandledLoginView(APIView):
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
                pass
            return redirect('index')
        else:
            return render(request, 'login.html', {'message': 'Geçersiz kullanıcı adı veya şifre girişi yaptınız!'})

    def get(self, request):

        return render(request, 'login.html')

class CartView(APIView):
    @method_decorator(login_required)
    def get(self, request):
        orders = Order.objects.select_related('customer', 'product').filter(customer__user=request.user)
        total_price_sum = orders.aggregate(Sum('total_price'))['total_price__sum']
        total_item_count = orders.count()
        cargo_price = 20

        if total_price_sum and total_price_sum > 5000:
            cargo_price = 0

        order_serializer = OrderSerializer(orders, many=True, context={'request': request})

        context = {
            'orders': order_serializer.data,
            'total_price_sum': total_price_sum,
            'total_item_count': total_item_count,
            'cargo_price': cargo_price,
        }

        return render(request, "cart.html", context)

class AddToCartView(APIView):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)

        if request.method == 'POST':
            quantity = request.POST.get('quantity', '1')

            if request.user.is_authenticated:
                try:
                    customer = Customer.objects.get(user=request.user)
                    order = Order(
                        customer=customer,
                        product=product,
                        quantity=quantity,
                        total_price=product.price * int(quantity)
                    )
                    order.save()

                    product_serializer = ProductSerializer(product, context={'request': request})
                    customer_serializer = CustomerSerializer(customer)

                    return JsonResponse({
                        'message': 'Item was added to cart',
                        'product': product_serializer.data,
                        'customer': customer_serializer.data
                    })
                except Customer.DoesNotExist:
                    return JsonResponse({'message': 'Kullanıcı hiçbir müşteriye sahip değil'})
            else:
                return JsonResponse({'message': 'Yetkisiz kullanıcı!'})

        return redirect('index')

def delete_order(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('cart')


def add_comment(request, product_id):
    url = request.META.get("HTTP_REFERER") #bir önceki url i alır
    customer = Customer.objects.get(user=request.user)
    product = get_object_or_404(Product, id=product_id)

    checkCompletedOrder = Order.objects.select_related('customer').get(customer=customer.id).is_completed
    if checkCompletedOrder:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                customer=customer,
                product=product,
                comment=form.cleaned_data['comment'],
                rate=form.cleaned_data['rate'],
            )
            comment.save()
            return redirect(url)
        
        print(form.errors)
    return redirect("index") 


class ProductDetailView(APIView):
    @method_decorator(login_required)
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        customer, created = Customer.objects.get_or_create(user=request.user)
        total_item_count = Order.objects.filter(customer=customer).count()
        
        product_serializer = ProductSerializer(product, context={'request': request})
        comments = Comment.objects.select_related('customer', 'product').filter(product = product_id)
        print("///")
        print(customer)

        return render(request, 'detail.html', {'comments':comments,'product': product_serializer.data, 'total_item_count': total_item_count,})

    @method_decorator(login_required)
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        customer, created = Customer.objects.get_or_create(user=request.user)

        if request.method == 'POST':
            quantity = int(request.POST.get('quantity', 1))
            try:
                order = Order.objects.select_related('customer', 'product').get(customer=customer, product=product)
                order.quantity += quantity
                order.total_price = product.price * order.quantity
                order.save()
            except Order.DoesNotExist:
                order = Order(
                    customer=customer,
                    product=product,
                    quantity=quantity,
                    total_price=product.price * quantity
                )
                order.save()
            return redirect('cart')

class CheckoutView(APIView):
    @method_decorator(login_required)
    def get(self, request):
        customer = get_object_or_404(Customer, user=request.user)
        orders = Order.objects.filter(customer=customer).prefetch_related('product')

        if not orders.exists():
            return redirect('index')

        total_price_sum = orders.aggregate(Sum('total_price'))['total_price__sum']
        total_item_count = orders.count()


        context = {
            'total_item_count': total_item_count,
            'total_price_sum': total_price_sum,
        }

        if get_customer_from_cookie(request):
            return render(request, 'address_form.html', context)
        else:
            return render(request, 'login.html')

    @method_decorator(login_required)
    def post(self, request):
        customer = get_object_or_404(Customer, user=request.user)
        orders = Order.objects.filter(customer=customer).prefetch_related('product')
        if not orders.exists():
            return redirect('index')
        total_price_sum = orders.aggregate(Sum('total_price'))['total_price__sum']
        total_item_count = orders.count()

        context = {
            'total_item_count': total_item_count,
            'total_price_sum': total_price_sum,

        }
        if get_customer_from_cookie(request):
            return render(request, 'address_form.html', context)
        else:
            return render(request, 'login.html')

stripe.api_key = settings.STRIPE_SECRET_KEY
checkout_session = stripe.checkout.Session.create(
        payment_method_types=[
            'card',
        ],
        line_items=[
            {
                'price': 'price_1NRMgrDGClv24mi8EMjZuTe7',
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url='http://127.0.0.1:5555/success',
        cancel_url='http://127.0.0.1:5555/',
    )

@login_required
def payment_checkout(request):

    customer = get_object_or_404(Customer, user=request.user)
    orders = Order.objects.filter(customer=customer).prefetch_related('product')

    order = orders.latest('created_at')
        
    address_line1 = request.POST.get('address_line1')
    address_line2 = request.POST.get('address_line2')
    city = request.POST.get('city')
    state = request.POST.get('state')
    postal_code = request.POST.get('postal_code')

    address = Address(
        customer=customer,
        order=order,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        postal_code=postal_code
    )
    address.save()

    if checkout_session['payment_status'] == 'unpaid':
        checkout_session['payment_status'] = 'paid'

    return redirect(checkout_session.url, code=303)

#STOKTAN DUSME 
def success_view(request):
    print(checkout_session['payment_status'])
    if checkout_session['payment_status'] == 'paid':
        addresses = Address.objects.all().select_related('order') 
        for address in addresses:
            quantity = address.order.product.stock

            print(address.order.quantity)
            print(address.order.product.id)
            print(quantity)

            product = Product.objects.get(id=address.order.product.id)
            product.stock = quantity - address.order.quantity
            product.save()
            checkout_session['payment_status'] = 'unpaid'
            Order.objects.filter(product=product).update(is_completed = True) 
            return render(request, 'success.html')
        
    else:
        return render(request, 'success.html')
    
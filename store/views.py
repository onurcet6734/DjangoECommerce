from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Order, Customer, Address
from django.http import JsonResponse
from django.db.models import Sum
from .utils import set_customer_cookie, get_customer_from_cookie, delete_customer_cookie


def index(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get('category_id')
    if category_id:
        products = products.filter(category_id=category_id)

    total_item_count = Order.objects.filter(user=request.user).count()

    context = {
        'products': products,
        'categories': categories,
        'total_item_count': total_item_count
    }
    return render(request, "index.html", context)


def cart(request):
    orders = Order.objects.filter(user=request.user)
    total_price_sum = Order.objects.filter(user=request.user).aggregate(Sum('total_price'))['total_price__sum']
    total_item_count = orders.count()

    context = {
        'orders': orders,
        'total_price_sum': total_price_sum,
        'total_item_count': total_item_count,
        'categories': Category.objects.all(),
    }
    return render(request, "cart.html", context)


def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)

    if request.method == 'POST':
        quantity = request.POST.get('quantity', '1')

        order = Order(
            user=request.user,
            product=product,
            quantity=quantity,
            total_price=product.price * int(quantity)
        )
        order.save()

        return JsonResponse({'message': 'Item was added to cart'})


def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('cart')


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        try:
            order = Order.objects.get(user=request.user, product=product)
            order.quantity += quantity
            order.total_price = product.price * order.quantity
            order.save()
        except Order.DoesNotExist:
            order = Order(
                user=request.user,
                product=product,
                quantity=quantity,
                total_price=product.price * quantity
            )
            order.save()

        return redirect('cart')

    total_item_count = Order.objects.filter(user=request.user).count()

    return render(request, 'detail.html', {'product': product, 'total_item_count': total_item_count,  'categories': Category.objects.all()})


def checkout(request):
    if request.method == 'POST':
        order = Order.objects.filter(user=request.user).latest('created_at')
        customer = get_object_or_404(Customer, user=request.user)  # Customer informartion
        total_price_sum = request.POST.get('total_price_sum', 0)
        address = Address(
            customer=customer,
            order=order,
            address_line1=request.POST['address_line1'],
            address_line2=request.POST['address_line2'],
            city=request.POST['city'],
            state=request.POST['state'],
            postal_code=request.POST['postal_code']
        )
        address.save()
        return redirect('payment')  # Payment Page
    
    order = Order.objects.filter(user=request.user).latest('created_at')
    total_price_sum = Order.objects.filter(user=request.user).aggregate(Sum('total_price'))['total_price__sum']

    context = {
        'order': order,
        'total_price_sum': total_price_sum,
    }
    return render(request, 'address_form.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Order
from django.http import JsonResponse

def index(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get('category_id')
    if category_id:
        products = products.filter(category_id=category_id)

    context = {
        'products': products,
        'categories': categories
    }
    return render(request, "index.html", context)

def cart(request):
    orders = Order.objects.filter(user=request.user)

    context = {
        'orders': orders
    }
    return render(request, "cart.html", context)

def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)

    if request.method == 'POST':
        quantity = request.POST.get('quantity', '1')  # default values is '1' s

        # Create an Order instance and save it to the database
        order = Order(
            user=request.user,
            product=product,
            quantity=quantity,
            total_price=product.price * int(quantity)
        )
        order.save()

        return JsonResponse({'message': 'Item was added to cart'})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        # Check if the product is already in the user's cart
        try:
            order = Order.objects.get(user=request.user, product=product)
            order.quantity += quantity
            order.total_price = product.price * order.quantity
            order.save()
        except Order.DoesNotExist:
            # Create a new Order instance and save it to the database
            order = Order(
                user=request.user,
                product=product,
                quantity=quantity,
                total_price=product.price * quantity
            )
            order.save()

        return redirect('cart')

    return render(request, 'detail.html', {'product': product})

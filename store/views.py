from django.shortcuts import render, get_object_or_404,redirect
from .models import Category, Product, Order
from django.contrib import messages

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

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    
    context = {
        'product': product,'categories': categories
    }
    return render(request, 'detail.html', context)

def cart(request):
    orders = Order.objects.filter(user=request.user)
    
    context = {
        'orders': orders
    }
    return render(request, "cart.html", context)


def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        product = Product.objects.get(pk=product_id)
        
        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            total_price=product.price * quantity,
            address=request.user.customer.address,
        )
        
        messages.success(request, f"{product.title} sepete eklendi.")
        
        return redirect('cart')
        


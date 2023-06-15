from django.shortcuts import render, get_object_or_404,redirect
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


def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)

    if request.method == 'POST':
        quantity = request.POST.get('quantity', '1')  # Varsayılan değer olarak '1' kullanılıyor
       

        cart = request.session.get('cart', [])
        cart.append({
            'product_id': product.id,
            'quantity': quantity
        })
        request.session['cart'] = cart
        print(product_id)
        return JsonResponse('Item was added')

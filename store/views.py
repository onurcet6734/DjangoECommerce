from django.shortcuts import render, get_object_or_404,redirect
from .models import Category, Product

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

def card(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    context = {
        'product': product
    }
    return render(request, "card.html", context)


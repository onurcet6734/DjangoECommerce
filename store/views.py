from django.shortcuts import render, get_object_or_404
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

def detail_view(request):
    return render(request, 'details.html')

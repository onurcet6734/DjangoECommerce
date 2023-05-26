from django.shortcuts import render
from .models import Category, Product

def index(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    context = {'products': products, 'categories': categories}
    return render(request, "index.html", context)

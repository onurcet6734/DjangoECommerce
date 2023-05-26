from django.shortcuts import render,get_object_or_404
from .models import Category, Product

def index(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    context = {'products': products, 'categories': categories}
    return render(request, "index.html", context)

def detail_view(request):
    return render(request, 'details.html')
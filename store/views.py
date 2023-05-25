from django.shortcuts import render
from .models import *

def index(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request,"index.html",context)


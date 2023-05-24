from django.shortcuts import render, get_object_or_404, redirect
from .models import Product

def index(request):
    return render(request, 'index.html')

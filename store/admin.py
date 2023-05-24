from django.contrib import admin
from .models import Category, Product, Address, Order, Payment

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(Payment)

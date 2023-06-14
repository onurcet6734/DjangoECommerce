from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:product_id>/', views.product_detail, name='detail'),
    path('cart/<int:product_id>/', views.cart, name='cart'),
    path('cart/', views.cart, name='cart'),  # Add this line for the cart page
]

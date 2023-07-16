from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('indexAPI/', views.indexApi, name='index'),
    path('detail/<int:product_id>/', views.product_detail, name='detail'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('address-form/', views.checkout, name='checkout'),
    path('login/', views.handledLogin, name='handledLogin'),
    path('payment_checkout/', views.payment_checkout, name='payment_checkout'),





 

]
    
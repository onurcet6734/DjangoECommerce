from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('indexAPI/', views.IndexApiView.as_view()),
    path('detail/<int:product_id>/', views.ProductDetailView.as_view(), name='detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add-to-cart/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('address-form/', views.CheckoutView.as_view(), name='checkout'),
    path('login/', views.HandledLoginView.as_view(), name='handledLogin'),
    path('payment_checkout/', views.payment_checkout, name='payment_checkout'),
]

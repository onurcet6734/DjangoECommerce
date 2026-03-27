from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    IndexView,
    RegisterView,
    HandledLoginView,
    CartView,
    DeleteOrderView,
    ProductDetailView,
    AddCommentView,
    CheckoutView,
    PaymentCheckoutView,
    SuccessView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("logout/", LogoutView.as_view(next_page="index"), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("accounts/login/", HandledLoginView.as_view(), name="handledLogin"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/delete/<int:order_id>/", DeleteOrderView.as_view(), name="delete_order"),
    path("product/<int:product_id>/", ProductDetailView.as_view(), name="product_detail"),
    path("product/<int:product_id>/comment/", AddCommentView.as_view(), name="add_comment"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("checkout/payment/", PaymentCheckoutView.as_view(), name="payment_checkout"),
    path("success/", SuccessView.as_view(), name="success"),
]
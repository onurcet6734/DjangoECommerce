from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:product_id>/', views.product_detail, name='detail'),
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),
]

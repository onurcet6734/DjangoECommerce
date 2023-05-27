from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:product_id>/', views.product_detail, name='detail'),
    path('card/<int:product_id>/', views.card, name='card'),
]

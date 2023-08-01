from django.urls import path
from store.api.views import (ProductListAPIView,CategoryCreateAPIView,ProductDestroyAPIView,ProductUpdateAPIView)

urlpatterns = [
    path('api/product/list/', ProductListAPIView.as_view()),
    path('api/category/create/', CategoryCreateAPIView.as_view()),
    path('api/product/update/<int:pk>', ProductUpdateAPIView.as_view()),
    path('api/product/delete/<int:pk>', ProductDestroyAPIView.as_view()),

]

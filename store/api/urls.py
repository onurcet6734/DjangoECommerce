from django.urls import path
from store.api.views import (ProductListAPIView,CategoryCreateAPIView,PostUpdateAPIView)

urlpatterns = [
    path('api/product/list/', ProductListAPIView.as_view()),
    path('api/product/update/<int:pk>', PostUpdateAPIView.as_view()), #update-delete operations
    path('api/category/create/', CategoryCreateAPIView.as_view()),

]

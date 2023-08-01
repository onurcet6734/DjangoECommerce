from django.urls import path
from store.api.views import (ProductListAPIView,)

urlpatterns = [
    path('api/product/list/', ProductListAPIView.as_view()),

]

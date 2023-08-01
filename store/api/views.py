
from store.models import Product
from store.api.serializers import ProductSerializer
from rest_framework.generics import ListAPIView


class ProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

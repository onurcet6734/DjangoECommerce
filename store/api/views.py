
from store.models import Product, Category
from store.api.serializers import ProductSerializer, CategorySerializer
from rest_framework.generics import ListAPIView,CreateAPIView,RetrieveUpdateAPIView,ListCreateAPIView
from rest_framework.mixins import DestroyModelMixin



class ProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryCreateAPIView(CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class PostUpdateAPIView(RetrieveUpdateAPIView, DestroyModelMixin):
    queryset = Product.objects.all()  
    serializer_class = ProductSerializer
    lookup_field = 'pk'
    

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)
    

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    

class ProductListCreateAPIView(ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.all()

    def perform_create(self, serializer):
        serializer.save()

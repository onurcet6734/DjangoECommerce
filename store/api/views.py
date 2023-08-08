
from store.models import Product, Category
from store.api.serializers import ProductSerializer, CategorySerializer
from rest_framework.generics import ListAPIView, DestroyAPIView,UpdateAPIView,CreateAPIView,RetrieveUpdateAPIView
from rest_framework.mixins import DestroyModelMixin



class ProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryCreateAPIView(CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class PostUpdateAPIView(RetrieveUpdateAPIView, DestroyModelMixin):
    queryset = Product.objects.all()  # queryset tanımlaması
    serializer_class = ProductSerializer
    lookup_field = 'pk'
    
    # perform_update() metoduyla güncelleme işlemi gerçekleştiriliyor
    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)
    
    # delete() metoduyla silme işlemi gerçekleştiriliyor
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
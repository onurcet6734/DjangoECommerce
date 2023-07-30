
from store.models import Product
from store.api.serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


class IndexApiView(APIView):
    def get(self, request):
        products = Product.objects.select_related('category').all()
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
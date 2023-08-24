from store.models import Category
from store.api.serializers import CategorySerializer

def nav_data(request):
     category_serializer = CategorySerializer(Category.objects.all(), many=True)
     context = {'categories': category_serializer.data,}
     return context
      
            
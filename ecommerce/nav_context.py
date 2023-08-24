from store.models import Category
from store.api.serializers import CategorySerializer
from store.utils import get_customer_from_cookie

def nav_data(request):
     category_serializer = CategorySerializer(Category.objects.all(), many=True)
     customer_from_cookie = get_customer_from_cookie(request)
     context = {'categories': category_serializer.data,'customer_from_cookie': customer_from_cookie,}
     return context
      
            
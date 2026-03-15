from store.models import Category

def nav_data(request):
    categories = Category.objects.all()
    customer_from_cookie = request.COOKIES.get('customer_id')

    context = {
        "categories": categories,
        "customer_from_cookie": customer_from_cookie,
    }
    return context
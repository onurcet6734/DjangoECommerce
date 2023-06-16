from django.http import HttpResponse
from .models import Customer

def get_customer_from_cookie(request):
    customer_id = request.COOKIES.get('customer_id')
    if customer_id:
        customer = Customer.objects.get(id=customer_id)
        return customer
    return None

def set_customer_cookie(response, customer_id):
    response.set_cookie('customer_id', customer_id)

def delete_customer_cookie(response):
    response.delete_cookie('customer_id')

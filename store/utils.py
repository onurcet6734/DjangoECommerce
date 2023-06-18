from django.http import HttpResponse

def set_customer_cookie(response, customer_id):
    response.set_cookie('customer_id', customer_id)

def get_customer_from_cookie(request):
    customer_id = request.COOKIES.get('customer_id')
    return customer_id

def delete_customer_cookie(response):
    response.delete_cookie('customer_id')
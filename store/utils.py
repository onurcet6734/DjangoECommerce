from django.http import HttpResponse

def set_customer_cookie(response, customer_id):
    response.set_cookie('customer_id', customer_id)

def get_customer_from_cookie(request):
    customer_id = request.COOKIES.get('customer_id')
    return customer_id

def delete_customer_cookie(response):
    response.delete_cookie('customer_id')

# from django.http import HttpResponse
# from rest_framework_jwt.utils import jwt_decode_handler, jwt_encode_handler
# from rest_framework_jwt import utils as jwt_utils
# import datetime

# def set_customer_jwt(response, customer_id):
#     payload = {
#         'customer_id': customer_id,
#         'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  
#     }
#     token = jwt_encode_handler(payload)
#     response.set_cookie('jwt_token', token, httponly=True)

# def get_customer_from_jwt(request):
#     token = request.COOKIES.get('jwt_token')
#     if token:
#         try:
#             payload = jwt_decode_handler(token)
#             return payload['customer_id']
#         except jwt_utils.ExpiredSignatureError:
#             return None
#     return None

# def delete_customer_jwt(response):
#     response.delete_cookie('jwt_token')
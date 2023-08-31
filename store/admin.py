from django.contrib import admin
from .models import Customer,Category, Product, Address, Order,Comment#,Payment, 


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','customer','product','comment','rate')
    list_display_links = ('id','customer')
    list_filter = ('comment',)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id','name')

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Comment, CommentAdmin)
# admin.site.register(Payment)
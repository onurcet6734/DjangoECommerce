from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, default='Default Name')
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
    def update_name_from_user(self):
        if self.user:
            self.name = self.user.username
            self.save()


class Product(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    stock = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    image = models.ImageField(null=True, blank=True)


    def __str__(self):
        return self.title


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True,  editable=False)
    is_admin_product = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)  
  


    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity

        if self.customer and self.customer.user and self.customer.user.username == 'admin':
            self.is_admin_product = True
        else:
            self.is_admin_product = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.pk}"


class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}"

    
class Comment(models.Model):
    RATE_CHOICES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),)  
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    subject = models.CharField(max_length=50,blank=True)
    comment = models.TextField(max_length=200,blank=True)
    rate = models.IntegerField(choices=RATE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,  editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return f"{self.comment}->{self.product}"


# class Payment(models.Model):
#     order = models.OneToOneField(Order, on_delete=models.CASCADE)
#     payment_method = models.CharField(max_length=100, blank=False)
#     transaction_id = models.CharField(max_length=100, blank=False)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Payment for Order #{self.order.pk}"
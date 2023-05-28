from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200)

	def __str__(self):
		return self.name


class Product(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    image = models.ImageField(null=True, blank=True)


    def __str__(self):
        return self.title


class Address(models.Model):
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order #{self.pk}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)



class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100, blank=False)  
    transaction_id = models.CharField(max_length=100, blank=False)  
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.pk}"

from django.db import models
from customer.models import Customer
from product.models import Product

class Order(models.Model):
    customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=200)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.customer.name} ordered {self.product.name}"
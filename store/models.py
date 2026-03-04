from django.db import models
from datetime import date
import uuid

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return self.name
    
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True)
    date = models.DateField(default=date.today)
    customer_name = models.CharField(max_length=100)
    total = models.IntegerField(default=0)

    def __str__(self):
        return self.invoice_number
    
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        related_name="items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    subtotal = models.IntegerField()
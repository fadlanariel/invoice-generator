from django.db import models
from datetime import date

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return self.name
    
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    date = models.DateField(default=date.today)
    customer_name = models.CharField(max_length=100)
    total = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.invoice_number:
            self.invoice_number = f"INV-{self.date.strftime('%Y%m%d')}-{self.pk:05d}"
            super().save(update_fields=["invoice_number"])

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
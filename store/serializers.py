from rest_framework import serializers
from .models import Product, Invoice, InvoiceItem
import uuid

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class InvoiceItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = InvoiceItem
        fields = ['product_id', 'quantity']

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'date', 'customer_name', 'total', 'items']
        read_only_fields = ['invoice_number', 'total']

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        invoice_number = f"INV-{uuid.uuid4().hex[:6]}"

        invoice = Invoice.objects.create(
            invoice_number = invoice_number,
            **validated_data
        )

        total = 0

        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            quantity = item_data['quantity']
            subtotal = product.price * quantity
            total += subtotal

            InvoiceItem.objects.create(
                invoice = invoice,
                product = product,
                quantity = quantity,
                subtotal = subtotal
            )
        
        invoice.total = total
        invoice.save()

        return invoice
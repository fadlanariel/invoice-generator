from rest_framework import serializers
from .models import Product, Invoice, InvoiceItem
import uuid

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class InvoiceItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceItem
        fields = ["product_id", "product_name", "quantity", "price", "subtotal"]

    def get_subtotal(self, obj):
        return obj.quantity * obj.product.price


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ["id", "invoice_number", "date", "customer_name", "total", "items"]
        read_only_fields = ["invoice_number", "total"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")

        # Create invoice first (invoice_number will be generated in model.save())
        invoice = Invoice.objects.create(**validated_data)

        total = 0

        for item_data in items_data:
            product = Product.objects.get(id=item_data["product_id"])
            quantity = item_data["quantity"]

            subtotal = product.price * quantity
            total += subtotal

            InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=quantity,
                subtotal=subtotal,
            )

        invoice.total = total
        invoice.save()

        return invoice
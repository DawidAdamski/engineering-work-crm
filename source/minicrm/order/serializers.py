from rest_framework import serializers
from .models import Order, OrderItem
from customer.models import Customer
from product.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'order_date', 'total_price', 'items']
        read_only_fields = ['id', 'order_date', 'total_price']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total = 0
        for item in items_data:
            product = item['product']
            quantity = item['quantity']
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
            total += product.price * quantity
        order.total_price = total
        order.save()
        return order

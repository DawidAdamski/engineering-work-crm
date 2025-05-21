from django.shortcuts import render
from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-order_date')
    serializer_class = OrderSerializer
    lookup_field = 'id'
    lookup_value_regex = '[0-9a-f-]{36}'

# Create your views here.

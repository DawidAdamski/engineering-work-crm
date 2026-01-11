from rest_framework import serializers
from .models import RFMScore
from customer.serializers import CustomerSerializer


class RFMScoreSerializer(serializers.ModelSerializer):
    """Serializer for RFM Score model."""
    
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.UUIDField(write_only=True, required=False)
    rfm_code = serializers.CharField(read_only=True)
    
    class Meta:
        model = RFMScore
        fields = [
            'customer',
            'customer_id',
            'recency_days',
            'frequency',
            'monetary',
            'recency_score',
            'frequency_score',
            'monetary_score',
            'segment',
            'rfm_code',
            'calculated_at'
        ]
        read_only_fields = ['calculated_at', 'rfm_code']


class RFMScoreListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list view."""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    rfm_code = serializers.CharField(read_only=True)
    
    class Meta:
        model = RFMScore
        fields = [
            'customer_id',
            'customer_name',
            'customer_email',
            'recency_score',
            'frequency_score',
            'monetary_score',
            'rfm_code',
            'segment',
            'recency_days',
            'frequency',
            'monetary',
            'calculated_at'
        ]
        read_only_fields = ['customer_id', 'calculated_at', 'rfm_code']

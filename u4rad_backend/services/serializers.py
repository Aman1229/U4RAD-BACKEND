from rest_framework import serializers
from .models.models import Service, ServiceRate

class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRate
        fields = ['min_quantity', 'max_quantity', 'rate']

class ServiceSerializer(serializers.ModelSerializer):
    rates = RateSerializer(many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'service_name', 'rates']

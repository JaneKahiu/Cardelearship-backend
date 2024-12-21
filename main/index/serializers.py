from rest_framework import serializers
from .models import Customer, Inquiry, Car

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = '__all__'
class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'  
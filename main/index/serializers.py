from rest_framework import serializers
from .models import Customer, Inquiry, Car
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User

class UserSerializer(ModelSerializer):
    confirmPassword = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmPassword']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, data):
        """
        Ensure the passwords are the same
        """
        if data['password'] !=data['confirmPassword']:
            raise serializers.ValidationError({"confirmPassword": "Passwords do not match."})
        return data
    def create(self, validated_data):
        """Remove confirmPassword before saving the user"""
        validated_data.pop('confirmPassword')
        return User.objects.create_user(**validated_data)


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
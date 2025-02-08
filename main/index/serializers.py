from rest_framework import serializers
from .models import  Inquiry, Car,User,Profile
from rest_framework.serializers import ModelSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get("password")

        user = authenticate(request=self.context.get("request"), email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")
        data = super().validate(attrs)
        data["full_name"] = user.profile.full_name
        data["username"] = user.username
        data["email"] = user.email
        return data
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['full_name'] = user.profile.full_name
        token['username'] = user.username
        token['email'] = user.email

        return token
    
class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password1 = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')  

        username = f"{first_name.lower()}{last_name.lower()}"

        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():  
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=validated_data['password1']
        )
        return user
    

class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = '__all__'
class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'  
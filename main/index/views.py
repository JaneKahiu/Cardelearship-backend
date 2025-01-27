from django.shortcuts import render ,redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, action
from rest_framework import status, viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .serializers import CustomerSerializer, InquirySerializer, CarSerializer, UserSerializer
from .models import Customer, Inquiry, Car
from rest_framework.permissions import AllowAny
from rest_framework import permissions
#customer profile view
class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       
        return super().get_queryset().filter(user=self.request.user)

    def perform_update(self, serializer):
        
        serializer.save(user=self.request.user)

    
    def retrieve(self, request, *args, **kwargs):
       
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    
    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
       
        customer = self.get_queryset().first()  
        if customer:
            serializer = self.get_serializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save()  
                return Response(serializer.data)  
            return Response(serializer.errors, status=400) 
        return Response({"error": "Profile not found."}, status=404)

#customer inquiry view
class InquiryListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(customer__user=self.request.user)

#search car view
class SearchCarViewSet(generics.ListAPIView):
    serializer_class = CarSerializer

    def get_queryset(self):
        queryset = Car.objects.all()
        #search by make
        make = self.request.query_params.get('make', None)
        if make:
            queryset = queryset.filter(make__icontains=make)
        #search by model
        model = self.request.query_params.get('model', None)
        if model:
            queryset = queryset.filter(model__icontains=model)
        #search by year
        year = self.request.query_params.get('year', None)
        if year:
            queryset = queryset.filter(year=year)
        #search by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price and max_price:
            queryset = queryset.filter(price__gte=min_price, price__lte=max_price)
        elif min_price:
            queryset = queryset.filter(price__gte=min_price)
        elif max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        Override the list method to handle search functionality and return results.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
#car specification view
class CarSpecificationsView(generics.RetrieveAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    lookup_field = 'pk'

    def get(self,request, *args, **kwargs):
        car = self.get_object()
        serializer = self.get_serializer(car)
        return Response(serializer.data)
#inquiry view
class MakeInquiryViewSet(generics.CreateAPIView):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAuthenticated] 
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)
#view inquiry list view
class ViewInquiryListView(generics.ListAPIView):
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Inquiry.objects.filter(customer=user.customer)
#carmangement view
class CarMangementViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
    def perform_update(self, serializer):
        serializer.save()

#customer management system view
class CustomerManagementViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
    def perform_update(self, serializer):
        serializer.save()

#Signup view    
logger = logging.getLogger(__name__)
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info(f"Signup request received with data: {request.data}")

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User {user.username} created successfully with email{user.email}")
            return Response ({'message': 'User created successfully', 'username':user.username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#Login view
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            data =json.loads(request.body)
        except json.loads(request.body):
            return JsonResponse({'message': 'Invalid request body'}, status=400)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'message': 'Username and password required'}, status=400)
        user = authenticate(username=username, password=password)
        if user:
            return redirect('/user-dashboard/')
        return JsonResponse({'message': 'Invalid credentials'}, status=400)

class UserDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self,request):
        username = request.user.username
        return JsonResponse({'message': f'Hello {username}, welcome to your dashboard'}, status=200)


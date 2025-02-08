from django.shortcuts import render ,redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework import status, viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .serializers import  UserSerializer,InquirySerializer, CarSerializer, MyTokenObtainPairSerializer, RegisterSerializer
from .models import  Inquiry, Car,User,Profile
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import permissions


from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = ([AllowAny])
    serializer_class = RegisterSerializer
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated]) 
def dashboard(request):
    if request.method == 'GET':
        response = f"Hello, {request.user.username}!"
        return Response({'response':response}, status=status.HTTP_200_OK)
    elif request.method == "POST":
        text = request.data.get("text")
        response = f"Hello, {request.user}, you text is: {text}"
        return Response({'response':response}, status=status.HTTP_200_OK)
    return Response({'response':'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
    def perform_update(self, serializer):
        serializer.save()

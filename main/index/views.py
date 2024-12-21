from django.shortcuts import render 
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, action
from rest_framework import status, viewsets, mixins, generics
from rest_framework.response import Response
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .serializers import CustomerSerializer, InquirySerializer, CarSerializer
from .models import Customer, Inquiry, Car
from rest_framework import permissions
#customer profile view
class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter to get only the profile of the authenticated user
        return super().get_queryset().filter(user=self.request.user)

    def perform_update(self, serializer):
        # Ensure that the updated data is saved for the current user
        serializer.save(user=self.request.user)

    # Override the `retrieve` method to ensure it only returns the current user's profile
    def retrieve(self, request, *args, **kwargs):
        # Since `get_queryset` already filters by the current user, `retrieve` will only return that user's profile.
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # Optionally, you can create a custom action for updating the profile (though `perform_update` already handles PUT)
    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        # Ensure only the current user can update their profile
        customer = self.get_queryset().first()  # Get the authenticated user's profile
        if customer:
            serializer = self.get_serializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save()  # Save the updated profile
                return Response(serializer.data)  # Return the updated profile data
            return Response(serializer.errors, status=400)  # Return validation errors if any
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
    lookup_field = 'pk'#lookup by the primarykey

    def get(self,request, *args, **kwargs):
        car = self.get_object()
        serializer = self.get_serializer(car)#serialize the car object
        return Response(serializer.data)#return the serialized data as response
#inquiry view
class MakeInquiryViewSet(generics.CreateAPIView):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAuthenticated] #ensure the user is authenticated to make an inquiry

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





# Setting up a logger
logger = logging.getLogger(__name__)

# Setting up logger
logger = logging.getLogger(__name__)

@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        # Log the incoming request data
        logger.info(f"Signup request received with data: {request.data}")

        # Get data from the request
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        # Check for missing data
        if not username:
            return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email is already in use'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username is already taken'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the password
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return Response({'error': 'An error occurred while creating the user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Log user creation
        logger.info(f"User {username} created successfully with email {email}")

        # Print user creation success message
        print(f"User {username} created successfully with email {email}")

        # Return a success response with the username and message
        return Response({'message': 'User created successfully!', 'username': user.username}, status=status.HTTP_201_CREATED)

    # If the request method is not POST, return a 405 error
    return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

#login view
@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate (username=username, password=password)
        if user is not  None:
            return JsonResponse({'message': 'Login successfull!'})
        return JsonResponse({'error': 'Invalid credentials'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerProfileViewSet,
    InquiryListViewSet,
  
    SearchCarViewSet,
    CarSpecificationsView,
    MakeInquiryViewSet,
    ViewInquiryListView,
    CarMangementViewSet,
    CustomerManagementViewSet,
    SignupView,
    LoginView,
    UserDashboardView,
)

# Setting up the router for viewsets
router = DefaultRouter()
router.register(r'customer-profile', CustomerProfileViewSet, basename='customer-profile')
router.register(r'inquiry-list', InquiryListViewSet, basename='inquiry-list')
router.register(r'car-management', CarMangementViewSet, basename='car-management')
router.register(r'customer-management', CustomerManagementViewSet, basename='customer-management')

urlpatterns = [
    # Include router URLs
    path('api/', include(router.urls)),

    # Custom views
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/user-dashboard/', UserDashboardView.as_view(), name='user-dashboard'),
    path('api/search-cars/', SearchCarViewSet.as_view(), name='search-cars'),
    path('api/car-specifications/<int:pk>/', CarSpecificationsView.as_view(), name='car-specifications'),
    path('api/make-inquiry/', MakeInquiryViewSet.as_view(), name='make-inquiry'),
    path('api/view-inquiries/', ViewInquiryListView.as_view(), name='view-inquiries'),
]

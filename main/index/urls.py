from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import (
  
    InquiryListViewSet,
  
    SearchCarViewSet,
    CarSpecificationsView,
    MakeInquiryViewSet,
    ViewInquiryListView,
    CarMangementViewSet,
    CustomerManagementViewSet,
    MyTokenObtainPairView,
    RegisterView,
    dashboard,
)

# Setting up the router for viewsets
router = DefaultRouter()
router.register(r'inquiry-list', InquiryListViewSet, basename='inquiry-list')
router.register(r'car-management', CarMangementViewSet, basename='car-management')
router.register(r'customer-management', CustomerManagementViewSet, basename='customer-management')

urlpatterns = [
    # Include router URLs
    path('api/', include(router.urls)),

    # Custom views
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/',   RegisterView.as_view(), name='register'),
    path('api/user-dashboard/', dashboard, name='user-dashboard'),
    path('api/search-cars/', SearchCarViewSet.as_view(), name='search-cars'),
    path('api/car-specifications/<int:pk>/', CarSpecificationsView.as_view(), name='car-specifications'),
    path('api/make-inquiry/', MakeInquiryViewSet.as_view(), name='make-inquiry'),
    path('api/view-inquiries/', ViewInquiryListView.as_view(), name='view-inquiries'),
]
""
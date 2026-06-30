from django.urls import path
from users.views import (
    ArtisanRegisterView,
    CustomerRegisterView,
    # AdminCreateView,
    ArtisanViewSet,
    USSDView
)


urlpatterns = [
    path('artisan/register/', ArtisanRegisterView.as_view(), name='artisan-register'),
    path('customer/register/', CustomerRegisterView.as_view(), name='customer-register'),
    # path('admin/register/', AdminCreateView.as_view(), name='admin-register'),
    path('list-artisans/', ArtisanViewSet.as_view({'get': 'list'}), name='artisan-list'),
    path('ussd/', USSDView.as_view(), name='ussd'),
]
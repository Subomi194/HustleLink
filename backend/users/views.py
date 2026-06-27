from django.shortcuts import render
from rest_framework import generics, viewsets, status, permissions
from rest_framework.views import APIView
from users.models import ArtisanProfile, CustomerProfile
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from users.serializers import (
    ArtisanRegistrationSerializer,
    CustomerRegistrationSerializer,
    AdminRegistrationSerializer,
    ArtisanProfileSerializer)
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

User = get_user_model()

# Create your views here.
class ArtisanRegisterView(generics.CreateAPIView):
    serializer_class = ArtisanRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class CustomerRegisterView(generics.CreateAPIView):
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [permissions.AllowAny]

# class AdminCreateView(generics.CreateAPIView):
#     serializer_class = AdminRegistrationSerializer
#     permission_classes = [permissions.IsAdminUser]  

class ArtisanViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ArtisanProfileSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="List Artisans",
        responses={200: ArtisanProfileSerializer(many=True)},
        description="Retrieve a list of artisans. Filtering available with '?speciality='"
    )
    def get_queryset(self):
        user = self.request.user
        speciality = self.request.query_params.get('speciality')

        if not user.is_authenticated:
            # People on landing page sees all artisans on hustlelink
            queryset = ArtisanProfile.objects.filter(
                artisan__is_active=True
            )
        
        elif user.is_staff or user.role == 'admin':
            # Admin sees everything
            queryset = ArtisanProfile.objects.filter(
                artisan__is_active=True
            )

        else:
            # Safety check — artisans browsing shouldn't crash the app
            try:
                # looged in users only see artisans in their own state
                customer_profile = user.customer_profile
            except Exception:
                # if somehow an artisan hits this, just show their own state
                artisan_profile = user.artisan_profile
                queryset = ArtisanProfile.objects.filter(
                    artisan__is_active=True,
                    state=artisan_profile.state,
                    country=artisan_profile.country,
                )
            else:
                queryset = ArtisanProfile.objects.filter(
                    artisan__is_active=True,
                    state=customer_profile.state,
                    country=customer_profile.country,
                )
            
        if speciality:
            queryset = queryset.filter(speciality__icontains=speciality)

        return queryset



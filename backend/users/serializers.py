from rest_framework import serializers
from users.models import ArtisanProfile, CustomerProfile
from users.utils import normalize_phone
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field

User = get_user_model()

###Artisan
class ArtisanDetailSerializer(serializers.ModelSerializer):
    #Handles the profile portion only.
    location = serializers.SerializerMethodField()

    class Meta:
        model  = ArtisanProfile
        fields = ['specialities', 'city', 'state', 'location', 'country']

    @extend_schema_field(serializers.CharField)
    def get_location(self, obj):
        return f"{obj.city}, {obj.state}"

class ArtisanRegistrationSerializer(serializers.ModelSerializer):
   
    artisan_detail = ArtisanDetailSerializer(write_only=True)

    class Meta:
        model  = User
        fields = ['id', 'name', 'phone_number', 'artisan_detail', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_phone_number(self, value):
        try:
            return normalize_phone(value)
        except Exception:
            raise serializers.ValidationError(
                "Enter a valid phone number."
            )

    def create(self, validated_data):
        profile_data = validated_data.pop('artisan_detail')

        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            name=validated_data['name'],
            is_artisan=True, 
        )
        ArtisanProfile.objects.create(artisan=user, **profile_data)
        return user
    
    def to_representation(self, instance):
        
        profile = instance.artisan_profile  
        return {
            'id':           instance.id,
            'name':         instance.name,
            'phone_number': instance.phone_number,
            'created_at':   instance.created_at,
            'artisan_detail': ArtisanDetailSerializer(profile).data  
        }

class ArtisanProfileSerializer(serializers.ModelSerializer):
   
    name         = serializers.CharField(source='artisan.name')
    phone_number = serializers.CharField(source='artisan.phone_number')
    location     = serializers.SerializerMethodField()
    specialities = serializers.StringRelatedField(many=True)

    class Meta:
        model  = ArtisanProfile              
        fields = [
            'id', 'name', 'phone_number',
            'specialities', 'city', 'state', 'location', 'country'
        ]

    @extend_schema_field(serializers.CharField)
    def get_location(self, obj):
        return f"{obj.city}, {obj.state}"
    
###Customer
class CustomerDetailSerializer(serializers.ModelSerializer):

    location = serializers.SerializerMethodField()

    class Meta:
        model  = CustomerProfile
        fields = ['city', 'state', 'location', 'country']

    @extend_schema_field(serializers.CharField)
    def get_location(self, obj):
        return f"{obj.city}, {obj.state}"


class CustomerRegistrationSerializer(serializers.ModelSerializer):

    customer_detail = CustomerDetailSerializer(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'customer_detail', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_phone_number(self, value):
        try:
            return normalize_phone(value)
        except Exception:
            raise serializers.ValidationError(
                "Enter a valid phone number."
            )

    def create(self, validated_data):
        profile_data = validated_data.pop('customer_detail')

        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            name=validated_data['name'],
            is_customer=True, 
        )

        CustomerProfile.objects.create(customer=user, **profile_data)
        return user
    
    def to_representation(self, instance):

        profile = instance.customer_profile
        return {
            'id':           instance.id,
            'name':         instance.name,
            'phone_number': instance.phone_number,
            'created_at':   instance.created_at,
            'customer_detail': CustomerDetailSerializer(profile).data
        }
    
class CustomerProfileSerializer(serializers.ModelSerializer):
   
    name         = serializers.CharField(source='customer.name')
    phone_number = serializers.CharField(source='customer.phone_number')
    location     = serializers.SerializerMethodField()

    class Meta:
        model  = ArtisanProfile              
        fields = [
            'id', 'name', 'phone_number', 'city', 'state', 'location', 'country'
        ]
        
    @extend_schema_field(serializers.CharField)
    def get_location(self, obj):
        return f"{obj.city}, {obj.state}"
    
####admin to be continued
class AdminRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)  # never return password in response

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            role=User.Role.ADMIN,
            is_staff=True,  # allows access to Django admin panel
        )
        return user




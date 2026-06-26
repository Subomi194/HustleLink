from rest_framework import serializers
from users.models import ArtisanProfile, CustomerProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class ArtisanRegistrationSerializer(serializers.ModelSerializer):

    speciality = serializers.ChoiceField(choices=ArtisanProfile.specialisation.choices)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'speciality', 'city', 'state', 'country']

    def create(self, validated_data):
        profile_data = {
            'speciality': validated_data.pop('speciality'),
            'city': validated_data.pop('city'),
            'state': validated_data.pop('state'),
            'country': validated_data.pop('country')
        }

        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=User.Role.ARTISAN,
        )

        ArtisanProfile.objects.create(artisan=user, **profile_data)


class CustomerProfileSerializer(serializers.ModelSerializer):

    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'city', 'state', 'country']

    def create(self, validated_data):
        profile_data = {
            'city': validated_data.pop('city'),
            'state': validated_data.pop('state'),
            'country': validated_data.pop('country'),
        }

        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=User.Role.CUSTOMER,
        )

        CustomerProfile.objects.create(customer=user, **profile_data)

        return user
    
class AdminRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)  # never return password in response

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=User.Role.ADMIN,
            is_staff=True,  # allows access to Django admin panel
        )
        return user




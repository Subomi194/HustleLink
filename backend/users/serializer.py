from rest_framework import serializers
from users.models import ArtisanProfile, CustomerProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class ArtisanDetailSerializer(serializers.ModelSerializer):
    #Handles the profile portion only.
    location = serializers.SerializerMethodField()

    class Meta:
        model  = ArtisanProfile
        fields = ['speciality', 'city', 'state', 'location', 'country']

    def get_location(self, obj):
        return f"{obj.city}, {obj.state}"


class ArtisanRegistrationSerializer(serializers.ModelSerializer):
   
    artisan_detail = ArtisanDetailSerializer()

    class Meta:
        model  = User
        fields = ['id', 'name', 'phone_number', 'artisan_detail', 'created_at']

    def create(self, validated_data):
        profile_data = validated_data.pop('artisan_detail')

        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            name=validated_data['name'],
            role=User.Role.ARTISAN,
        )
        ArtisanProfile.objects.create(artisan=user, **profile_data)
        return user


class ArtisanProfileSerializer(serializers.ModelSerializer):
   
    name         = serializers.CharField(source='artisan.name')
    phone_number = serializers.CharField(source='artisan.phone_number')
    location     = serializers.SerializerMethodField()

    class Meta:
        model  = ArtisanProfile              
        fields = [
            'id', 'name', 'phone_number',
            'speciality', 'city', 'state', 'location', 'country'
        ]

    def get_location(self, obj):
        return f"{obj.city}, {obj.state}"
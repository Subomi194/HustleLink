from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, phone_number=None, email=None, password=None, **extra_fields):
        if not phone_number and not email:
            raise ValueError('Users must have a phone_number or email')
        
        if email:
            email = self.normalize_email(email)
        
        user = self.model(
            phone_number= phone_number,
            email=email,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)  # Set role to 'admin' for superusers

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        ARTISAN = 'artisan', 'Artisan'
        ADMIN = 'admin', 'Admin'

    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ARTISAN)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    email = models.EmailField(unique=True, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.phone_number or self.email or 'User'
    
class ArtisanProfile(models.Model):

    class Specialisation(models.TextChoices):
        PLUMBER = 'plumber', 'Plumber'
        ELECTRICIAN = 'electrician', 'Electrician'
        CARPENTER = 'carpenter', 'Carpenter'
        TAILOR = 'tailor', 'Tailor'
        HAIRSTYLIST = 'hairstylist', 'Hairstylist'
        BARBER = 'barber', 'Barber'
        MAKEUP_ARTIST = 'makeup_artist', 'Makeup Artist'

    artisan = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='artisan_profile')
    speciality = models.CharField(max_length=20, choices=Specialisation.choices)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.artisan.name}'s Profile"
    
class CustomerProfile(models.Model):
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.customer.name}'s Profile"
    

    

    

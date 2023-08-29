import random
import string
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
from django.db.models.signals import post_save
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionManager, BaseUserManager, PermissionsMixin, UserManager
)
import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone

from app_control.models import (Products, )

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        

        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")
        
        user = self.model(email = email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have a is_staff = True")

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have a is_superuser = True")

        if not email :
            raise ValueError("Email field is required")
        
        user = self.model(email = email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

        

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    first_name = models.CharField(max_length= 255, blank=True, null=True)
    last_name = models.CharField(max_length= 255, blank=True, null=True)
    username = models.CharField(max_length= 255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    last_seen = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Tokens(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    
class Transaction(models.Model):
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.JSONField(null=True, blank=True)
    status = models.CharField(choices=[[FAILED]*2, [SUCCESS]*2, [PENDING]*2], max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def clean(self):
        if self.tokens < 0:
            raise ValidationError("Tokens cannot be lower than 0.")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}: Payment: {self.status}"
        
# class Cards(models.Model):

#     def validate_expiry_date(value):
#         try:
#             month, year = value.split('/')
#             expiry_date = timezone.datetime(int(year), int(month), 1, tzinfo=timezone.utc)
#             if expiry_date < timezone.now():
#                 raise ValidationError("Expiry date must be in the future.")
#         except ValueError:
#             raise ValidationError("Expiry date should be in the format MM/YYYY.")
#     id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)

#     card_number = models.CharField(max_length=255)
#     cvc = models.CharField(max_length=255)
#     card_holder = models.CharField(max_length=255)
#     source = models.JSONField(null=True, blank=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     expiry_date = models.CharField(max_length=7, validators=[validate_expiry_date])
    
#     created_at = models.DateTimeField(auto_now_add=True, editable=True)
#     updated_at = models.DateTimeField(auto_now=True, editable=True)
#     is_active = models.BooleanField(default=True)

# # Product Model
#     # id
#     # title
#     # description
#     # price
    
# class Customer(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
#     source = models.JSONField(null=True, blank=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     cards = models.ManyToManyField(Cards, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True, editable=True)
#     updated_at = models.DateTimeField(auto_now=True, editable=True)
#     is_active = models.BooleanField(default=True)

# class Accounts(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
#     account_id = models.CharField(max_length=255)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     cards = models.ManyToManyField(Cards, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True, editable=True)
#     updated_at = models.DateTimeField(auto_now=True, editable=True)

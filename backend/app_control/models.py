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

class Products(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    source = models.JSONField(null=True, blank=True)
    tokens = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    is_active = models.BooleanField(default=True)

    def __str__(self, *args, **kwargs):
        return self.title
    
class Message(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    response = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    is_active = models.BooleanField(default=True)
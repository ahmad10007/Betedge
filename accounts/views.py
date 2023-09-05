import random as rand
import random
import string
import jwt
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import SAFE_METHODS

from django.http import Http404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
# Create your views here.
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from rest_framework.decorators import api_view

from accounts.models import (User,
                             Transaction,
                             Tokens
                             )


from accounts.serializers import (UserSerializer,
                                  UserInfoSerializer,
                                  RegisterSerializer,
                                  TransactionSerializer,
                                  TransactionInfoSerializer,
                                  TokensSerializer,
                                  TokensInfoSerializer
                                )
from django.contrib.auth import authenticate
import logging
import stripe
import json
log = logging.getLogger("main")


from django.conf import settings

# class RegistrationViewSet(viewsets.ModelViewSet):
#     queryset = Registration.objects.filter(is_active=True)
#     filterset_fields = ['user', 'display', "portfolio", "projects", "portfolio", "events", "products", "services",
#                         "community", "walls", 'is_active', 'created_at', 'updated_at']

#     def get_serializer_class(self):
#         if self.request is None:
#             return RegistrationSerializer
#         elif not self.request.method in SAFE_METHODS:
#             return RegistrationSerializer
#         return RegistrationInfoSerializer


class RegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['post']

    queryset = User.objects.filter(is_active=True)
    filterset_fields = []

    def get_serializer_class(self):
        if self.request is None:
            return RegisterSerializer
        elif not self.request.method in SAFE_METHODS:
            return RegisterSerializer
        return RegisterSerializer
    

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['post']

    queryset = User.objects.filter(is_active=True)
    filterset_fields = []

    def get_serializer_class(self):
        if self.request is None:
            return TransactionSerializer
        elif not self.request.method in SAFE_METHODS:
            return TransactionSerializer
        return TransactionSerializer
    
    
def PaymentSuccessful(request, *args, **kwargs):
    try:
        trans = Transaction.objects.get(id = kwargs.get("id"))
    except Transaction.DoesNotExist:
        return Response(f"Transaction not found with this Id {kwargs.get('id')}")
    try:
        
        trans.status = Transaction.SUCCESS
        trans.save()
        token, created = Tokens.objects.get_or_create(user = trans.user)
        token.count = trans.product.tokens
        token.save()
                
        # Perform the redirect
        return redirect("http://127.0.0.1:8000")
    except Exception as e:
        log.error(f"Error on Payment Successful {e}")
        raise ValidationError(f"Error on Payment Successful {e}")
    
def verify(request, *args, **kwargs):
    token = AccessToken(kwargs.get("token"))
    try:
        log.info(token.payload)
        # Perform the redirect
        return redirect("http://127.0.0.1:8000")
    except Exception as e:
        log.error(f"Error on Payment Successful {e}")
        raise ValidationError(f"Error on Payment Successful {e}")
    
class VerifyEmailView(generics.GenericAPIView):
    serializer_class = Transaction

    def get(self, request):
        print("TOKEN")
        token = request.GET.get('token')
        token = RefreshToken(token)
        try:
            user = User.objects.get(id = token.payload["user_id"])
            user.is_verified = True
            user.save()
            RefreshToken(str(token)).blacklist()    
            return redirect("http://127.0.0.1:8000")
        except Exception as e:
            log.error(f"Error on Payment Successful {e}")
            raise ValidationError(f"Error on Payment Successful {e}")



class TokensViewSet(viewsets.ModelViewSet):
    serializer_class = TokensSerializer
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['get', "retrieve"]
    # http_method_names = ['retrieve']

    queryset = Tokens.objects.all().order_by('-created_at')
    filterset_fields = ["user", "id", "created_at", "updated_at"]

    def get_serializer_class(self):
        if self.request is None:
            return TokensSerializer
        elif not self.request.method in SAFE_METHODS:
            return TokensSerializer
        return TokensSerializer
    
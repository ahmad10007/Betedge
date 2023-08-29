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
from django.conf import settings


from app_control.models import (Products,
                                Message)

from app_control.serializers import (ProductsSerializer,
                                    ProductsInfoSerializer,
                                    MessageSerializer,
                                    MessageInfoSerializer)




class ProductViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.filter(is_active=True)
    filterset_fields = []

    def get_serializer_class(self):
        if self.request is None:
            return ProductsSerializer
        elif not self.request.method in SAFE_METHODS:
            return ProductsSerializer
        return ProductsSerializer

# class PaymentSuccessRedirectViewset(viewsets.ModelViewSet):
#     # queryset = Products.objects.filter(is_active=True)
#     # filterset_fields = []
#     http_method_names = ['get']

#     def get_serializer_class(self):
#         if self.request is None:
#             return PaymentSuccessSerializer
#         elif not self.request.method in SAFE_METHODS:
#             return PaymentSuccessSerializer
#         return PaymentSuccessSerializer


class MessageViewset(viewsets.ModelViewSet):
    # queryset = Products.objects.filter(is_active=True)
    # filterset_fields = []
    def get_serializer_class(self):
        if self.request is None:
            return MessageSerializer
        elif not self.request.method in SAFE_METHODS:
            return MessageSerializer
        return MessageSerializer

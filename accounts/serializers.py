from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer, HTMLFormRenderer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenVerifySerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.core.mail import send_mail
from datetime import datetime

from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from rest_framework.reverse import reverse_lazy


import logging
import stripe
import json
from django.http import HttpRequest
from app_control.models import (Products,)
from accounts.models import (User, Transaction, Tokens)

log = logging.getLogger("main")

class UserSerializer(serializers.ModelSerializer):
    tokens = serializers.SerializerMethodField(read_only=True)
    def get_tokens(self, obj):
        if obj.tokens_set.exists():
            return obj.tokens_set.first().count
        return 0
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', "tokens")

class UserInfoSerializer(serializers.ModelSerializer):

    tokens = serializers.SerializerMethodField(read_only=True)
    def get_tokens(self, obj):
        if obj.tokens_set.exists():
            return obj.tokens_set.first().count
        return 0

    class Meta:
        model = User
        depth = 1
        fields = ('id', 'email', 'first_name', 'last_name', "tokens")



class CustomJWTSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")  # Get the email from the input data
        password = attrs.get("password")

        # Authenticate user using email and password
        user = authenticate(request=self.context["request"], email=email, password=password)

        
        if user is None:
            raise AuthenticationFailed("No such user")


        if not user.is_verified:
            raise AuthenticationFailed("Please verify your email address to proceed")
            

        refresh = self.get_token(user)
        data = super().validate(attrs)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # Add extra responses here
        # profile = get_user_profile(self.user)
        # profile_serializer = get_user_profile_serializer(self.user)
        return {
            "user": UserSerializer(self.user).data,
            "refresh": str(data['refresh']),
            "access": str(data['access'])
        }


class CustomTokenVerifySerializer(TokenVerifySerializer):
    def validate(self, attrs):
        access_token_obj = AccessToken(attrs.get('token'))
        user_id = access_token_obj['user_id']
        user = User.objects.get(id=user_id)
        user.last_seen = datetime.now()
        user.save()
        # Add extra responses here
        if user.is_active:
            # profile = get_user_profile(user)
            # profile_serializer = get_user_profile_serializer(user)
            data = {"user": (UserSerializer(user).data,)}
            return {
                "data": data

            }
        else:
            return {
                "msg": "User not found"

            }


class RegisterSerializer(serializers.ModelSerializer):
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer, HTMLFormRenderer)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        """
        Hash value passed by user.
        :param value: password of a user
        :return: a hashed version of the password
        """
        return make_password(value)

    def create(self, validated_data):
        request = self.context["request"]
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user = User.objects.create(**validated_data)
        # user.is_verified = True
        user.is_verfied = False
        user.save()
        token = RefreshToken.for_user(user)  # Generate a JWT token
        r = HttpRequest()
        r.META['HTTP_HOST'] = self.context["request"].META["HTTP_HOST"]
        rev = reverse('verify')

        absolute_link = r.build_absolute_uri(rev)
        absolute_url = absolute_link+"?token="+str(token)

        # Send verification email
        subject = "Email Verification"
        message = f"Hi {user.first_name}, please verify your email by clicking the link:  {absolute_url}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        try:
            
            send_mail(subject, message, from_email, recipient_list)
            user.save()
            return user
        except Exception as e:
            user.delete()
            log.error(f"Can't create User {e}")
            raise serializers.ValidationError(f"Can't create User {e}")

        # user = User.objects.create(**validated_data)
        # token = RefreshToken.for_user(user)  # Generate a JWT token
        # r = HttpRequest()
        # r.META['HTTP_HOST'] = self.context["request"].META["HTTP_HOST"]
        # # verify_url = reverse('verify', request=request)

        # rev = reverse('verify')
        
        # absolute_link = r.build_absolute_uri(rev)
        # log.info(absolute_link+"?token="+str(token))
        # # log.info(absolute_link)
        # user.delete()
# class CardsSerializer(serializers.ModelSerializer):
#     localhosts = ["localhost:8000", "127.0.0.1:8000"]  
#     class Meta:
#         model = Cards
#         fields = ["card_number", "cvc", "card_holder", "user", "expiry_date", 'is_active', 'created_at', 'updated_at']
    
#     def create(self, validated_date, *args, **kwargs):
#         stripe.api_key = settings.STRIPE_SECRET_KEY
#         request = self.context["request"]
#         print("CARDS")
#         try:
#             card = Cards.objects.create(**validated_date)
#         except:
#             log.error("Can't create card for the user")
#             raise serializers.ValidationError("Can't create card for the user")

#         # Create Card
#         print(self.context["request"].META["HTTP_HOST"])
#         try:
#             if self.context["request"].META["HTTP_HOST"] not in self.localhosts:
#                 month, year = card.expiry_date.split("/")
#                 token = stripe.Token.create(
#                     card={
#                         "number": card.card_number,  # Replace with a valid card number
#                         "exp_month": int(month),
#                         "exp_year": int(year),
#                         "cvc": str(card.cvc),  
#                     },
#                 )
                
#                 card.source = token
#                 token_id = token.id
#             else:
#                 token_id = "tok_visa"
#         except Exception as e:
#             log.error(f"Can't create Card {e}" )
#             raise serializers.ValidationError(f"Can't create Card {e}")
            
#         try:
#             customer = card.user.customer_set.first() if card.user.customer_set.exists() else None
#             if customer:
#                 source = json.loads(customer.source)
#                 c = stripe.Customer.create_source(
#                     source["id"],
#                     source=token_id,
#                 )
#                 card.source =  json.dumps(c)
#                 card.save()
#                 card.user.customer_set.first().cards.add(card)
#                 card.user.customer_set.first().save()
#         except Exception as e:
#             log.error(f"Can't attach card to customer {e}")
#             raise serializers.ValidationError(f"Can't attach card to customer {e}")
#         return card
                     
            
        
            
# class CardsInfoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Cards
#         depth = 1
#         fields = ["card_number", "cvc", "card_holder", "user", "expiry_date", 'is_active', 'created_at', 'updated_at']



class TransactionSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()
    
    def get_link(self, obj, *args, **kwargs):
        source = json.loads(obj.source)
        return source["url"]
    
    def create(self, validated_data, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            if "user" in self.context["request"].data:
                user = User.objects.get(id = self.context["request"].data["user"])
            else:
                log.error("User is required to Create Link")
                raise serializers.ValidationError(f"User is required to Create Link")    
                
            if "product" in self.context["request"].data:
                product = Products.objects.get(id = self.context["request"].data["product"])
            else:
                log.error("Product is required to Create Link")
                raise serializers.ValidationError(f"Product is required to Create Link")    
            trans = Transaction.objects.create(user = user, product = product)
        except Exception as e: 
            log.error(f"Can't create Transaction: {e} ")
            raise serializers.ValidationError(f"Can't create Transaction: {e}")
        trans.status = Transaction.PENDING
        trans.save()
        
        try:
            source = json.loads(trans.product.source)
            r = HttpRequest()
            r.META['HTTP_HOST'] = self.context["request"].META["HTTP_HOST"]
            id = str(trans.id)
            rev = reverse('payment_successful', args=[str(id)])
            absolute_link = r.build_absolute_uri(rev)
            payment_link = stripe.PaymentLink.create(
                                                line_items = [
                                                    {
                                                        "price": source["id"],
                                                        "quantity": 1
                                                    }
                                                ],
                                                after_completion={"type": "redirect", "redirect": {"url": absolute_link}})
            print(payment_link)
            trans.source = json.dumps(payment_link)
            trans.save()
            return trans
        except Exception as e:
            trans.delete()
            log.error(f"Can't create Transaction: {e}")
            raise serializers.ValidationError(f"Can't create Transaction {e}")
            
        
    
    class Meta:
        model = Transaction
        fields = ["link"]

class TransactionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        depth = 1
        fields = "__all__"


class TokensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tokens
        fields = "__all__"

class TokensInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tokens
        depth = 1
        fields = "__all__"


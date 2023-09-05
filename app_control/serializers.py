from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer, HTMLFormRenderer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenVerifySerializer
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime
from django.conf import settings
import logging
import json
import stripe

from .models import (Products, Message)
log = logging.getLogger("main")

class ProductsSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    def create(self, validated_data, *args, **kwargs):
    
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if "price" in self.context["request"].data:
            price = self.context["request"].data.pop("price")
        else:
            log.error("Price is required for the Product")
            raise serializers.ValidationError("Price is required for the Product")

        try:
            product = Products.objects.create(**validated_data)
        except Exception as e:
            log.error(f"Could not create Product: {e}")
            raise serializers.ValidationError(f"Could not create Product: {e}")
        
        try:
            p = stripe.Product.create(name = product.title, description = product.description)
                        
            price = stripe.Price.create(unit_amount=price*100,
                                        currency="usd",
                                        product=p.id
                                        )
            product.source = json.dumps(price)
            product.save()
            return product
            
        except Exception as e:
            log.error(f"Could not create Product on Stripe: {e}")
            product.delete()
            raise serializers.ValidationError(f"Could not create Product on Stripe: {e}")
    
    def get_price(self, obj, *args, **kwargs):
        source = json.loads(obj.source)
        if "unit_amount" in source:
            return source["unit_amount"] / 100
        
    class Meta:
        model = Products
        fields = ["id","title", "description", "user", "position", "price", "tokens", "created_at", "updated_at", "is_active"] 
            
        
            
class ProductsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        depth = 1
        fields = "__all__"  



class MessageSerializer(serializers.ModelSerializer):
    # response = serializers.SerializerMethodField()
    tokens = serializers.SerializerMethodField(read_only = True)
    coins = serializers.CharField(write_only = True)
    
    def get_tokens(self, obj):
        if obj.user.tokens_set.exists():
            tokens = obj.user.tokens_set.first().count
            return tokens
        else:
            return 0

    def create(self, validated_data, *args, **kwargs):

        coins = validated_data.pop("coins", None)
        
        print(coins)
        
        try:
            msg = Message.objects.create(**validated_data)
        except Exception as e:
            log.error(f"Can't create Message: {e} ")
            raise serializers.ValidationError(f"Can't create Message: {e}")
        
        try:
            tokens = msg.user.tokens_set.first()
            if tokens.count == 0:
                msg.delete()
                raise serializers.ValidationError(f"You have insufficient tokens")
            elif tokens.count > int(coins):
                tokens.count -= int(coins)
                # msg.response = " Message saved Successfully"
                tokens.save()
                msg.save()
                return msg
            else:
                msg.delete()
                raise serializers.ValidationError(f"You must have {coins} tokens")
        except Exception as e:
            msg.delete()
            raise serializers.ValidationError(f"You don't have tokens to cosume")

    class Meta:
        model = Message
        fields = ["message", "response", "user", "tokens", "coins"]
        read_only_fields = ["tokens"]
        write_only_fields = ["coins"]

        
            
class MessageInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        depth = 1
        fields = "__all__"  





from rest_framework import routers
from django.urls import path, include

from accounts.views import (RegistrationViewSet, 
                            TransactionViewSet, 
                            PaymentSuccessful,
                            VerifyEmailView,
                            TokensViewSet)
from .serializers import CustomJWTSerializer, CustomTokenVerifySerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView

router = routers.DefaultRouter()
router.register(r'register', RegistrationViewSet, 'register')
router.register(r'transaction', TransactionViewSet, 'transaction')
router.register(r'tokens', TokensViewSet, 'tokens')
# router.register(r'cards', CardsViewSet, 'cards')


urlpatterns = [
    path('', include(router.urls)),

    # Registration 
    path('payment_successful/<str:id>/', PaymentSuccessful, name='payment_successful'),
    path('verify', VerifyEmailView.as_view(), name='verify'),
    path('login/', TokenObtainPairView.as_view(serializer_class=CustomJWTSerializer), name='login'),
    path('token-verify/', TokenVerifyView.as_view(serializer_class=CustomTokenVerifySerializer), name='token_verify'),

]

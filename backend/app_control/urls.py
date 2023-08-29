
from rest_framework import routers
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from app_control import views

router = routers.DefaultRouter()
router.register(r'products', views.ProductViewSet, 'products')
router.register(r'message', views.MessageViewset, 'messages')



urlpatterns = [
    path('', include(router.urls)),
    # path('payment_successful/<int:userId>/<int:productId>/', views.paymnet_successful, name='after_payment_successful'),

]
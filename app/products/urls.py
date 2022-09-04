from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet, basename="products")

urlpatterns = [
    path('register/', views.user_create),
    path('login/', obtain_auth_token),
]
urlpatterns += router.urls

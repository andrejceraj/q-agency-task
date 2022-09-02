from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.products, name="products"),
    path('products/<int:id>/', views.product, name="product"),
    path('products/<int:id>/rate-product/', views.rate_product, name="rate-product"),
]
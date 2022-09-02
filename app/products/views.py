from django.http import JsonResponse
from .models import Product, ProductRating
from .serializers import ProductSerializer, ProductRatingSerializer


def get_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return JsonResponse({"products": serializer.data})

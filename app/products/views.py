from datetime import datetime
from django.http import JsonResponse, HttpResponse
from .models import Product, ProductRating
from .serializers import ProductSerializer, ProductRatingSerializer
from rest_framework import response, status
from rest_framework.decorators import api_view


@api_view(["GET", "POST"])
def products(request):
    if request.method == "GET":
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return JsonResponse({"products": serializer.data})

    elif request.method == "POST":
        new_product = request.data
        new_product["rating"] = 0
        new_product["updated_at"] = datetime.now()
        serializer = ProductSerializer(data=new_product)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def product(request, id):

    try:
        product = Product.objects.get(pk=id)
    except:
        return response.Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ProductSerializer(product)
        return JsonResponse(serializer.data)

    elif request.method == "PUT":
        new_product = request.data
        new_product["rating"] = product.rating
        new_product["updated_at"] = datetime.now()
        serializer = ProductSerializer(product)
        serializer.update(product, new_product)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        product.delete()
        return HttpResponse(status=status.HTTP_200_OK)

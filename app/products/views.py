from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .models import Product, ProductRating
from .serializers import ProductSerializer, ProductRatingSerializer
from rest_framework import response, status
from rest_framework.decorators import api_view


@api_view(["GET", "POST"])
def products(request):
    if request.method == "GET":
        products = Product.objects.all()
        if request.GET.get("order_by"):
            order_value = request.GET.get("order_by")
            if request.GET.get("order") == "dsc":
                order_value = "-" + order_value
            products = products.order_by(order_value)

        per_page = request.GET.get("per_page", 10)
        page = request.GET.get("page", 1)
        paginator = Paginator(products, per_page)
        page_objects = paginator.get_page(page)
        serializer = ProductSerializer(page_objects, many=True)
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


@api_view(["POST"])
def rate_product(request, id):
    try:
        user = User.objects.get(username=request.data["username"])
    except:
        return JsonResponse({"status": "false", "message": "username not found"}, status=status.HTTP_404_NOT_FOUND)

    new_product_rating = {
        "user": user.id,
        "product": id,
        "value": request.data["value"],
    }
    serializer = ProductRatingSerializer(data=new_product_rating)
    if serializer.is_valid():
        serializer.save()
        product = Product.objects.get(pk=id)
        product_ratings = product.productrating_set.all()
        pr_sum = sum(list(map(lambda pr: pr.value, product_ratings)))
        product.rating = pr_sum / len(product_ratings)
        product.save()
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

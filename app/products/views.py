from datetime import datetime

from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

from .models import Product
from .serializers import (CreateUserSerializer, ProductRatingSerializer,
                          ProductSerializer)


class ProductViewSet(ViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request):
        products = Product.objects.all()
        if request.GET.get("order_by"):
            order_value = request.GET.get("order_by")
            if request.GET.get("order") == "dsc":
                order_value = "-" + order_value
            products = products.order_by(order_value)
        else:
            products = products.order_by("name")

        per_page = request.GET.get("per_page", 10)
        page = request.GET.get("page", 1)
        paginator = Paginator(products, per_page)
        page_objects = paginator.get_page(page)
        serializer = ProductSerializer(page_objects, many=True)
        return JsonResponse({"products": serializer.data})

    def create(self, request):
        new_product = request.data
        new_product["rating"] = 0
        new_product["updated_at"] = datetime.now()
        serializer = ProductSerializer(data=new_product)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        product = get_object_or_404(self.queryset, pk=pk)
        return JsonResponse(self.serializer_class(product).data)

    def update(self, request, pk=None):
        product = get_object_or_404(self.queryset, pk=pk)
        new_product = request.data
        new_product["rating"] = product.rating
        new_product["updated_at"] = datetime.now()
        serializer = ProductSerializer(product)
        serializer.update(product, new_product)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        product = get_object_or_404(self.queryset, pk=pk)
        product.delete()
        return HttpResponse(status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"], url_path="rate-product", permission_classes=[IsAuthenticated])
    def rate_product(self, request, pk=None):
        new_product_rating = {
            "user_id": request.user.id,
            "product_id": pk,
            "value": request.data["value"],
        }
        serializer = ProductRatingSerializer(data=new_product_rating)
        if serializer.is_valid():
            serializer.save()
            product = Product.objects.get(pk=pk)
            product_ratings = product.productrating_set.all()
            pr_sum = sum(list(map(lambda pr: pr.value, product_ratings)))
            product.rating = pr_sum / len(product_ratings)
            product.save()
            return JsonResponse(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_create(request):
    if request.method == 'POST':
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return HttpResponse(status=status.HTTP_201_CREATED)

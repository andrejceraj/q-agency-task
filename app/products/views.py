from datetime import datetime
from itertools import product

from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

from .models import Product
from .serializers import (CreateUserSerializer, ProductRatingRequestSerializer,
                          ProductRatingSerializer, ProductRequestSerializer,
                          ProductSerializer)


class ProductViewSet(ViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @extend_schema(parameters=[
        OpenApiParameter(
            name="per_page", description="Items per page", location="query"),
        OpenApiParameter(
            name="page", description="Current page number", location="query"),
        OpenApiParameter(
            name="order_by", description="Field by which the results are ordered", location="query"),
        OpenApiParameter(
            name="order", description="Ordering direction", location="query"),
    ])
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

    @extend_schema(request=ProductRequestSerializer)
    def create(self, request):
        create_serializer = ProductRequestSerializer(data=request.data)
        if create_serializer.is_valid():
            product = create_serializer.save()
            return JsonResponse(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(create_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        product = get_object_or_404(self.queryset, pk=pk)
        return JsonResponse(ProductSerializer(product).data)

    @extend_schema(request=ProductRequestSerializer)
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

    @extend_schema(request=ProductRatingRequestSerializer)
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


@extend_schema(request=CreateUserSerializer, responses={201: None})
@api_view(['POST'])
def user_create(request):
    if request.method == 'POST':
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return HttpResponse(status=status.HTTP_201_CREATED)

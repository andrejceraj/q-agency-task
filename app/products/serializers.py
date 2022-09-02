from rest_framework import serializers
from .models import Product, ProductRating


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "rating", "updated_at"]


class ProductRatingSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if data["value"] < 0 or data["value"] > 5:
            raise serializers.ValidationError({"value": "must be between 0 and 5"})
        return data

    class Meta:
        model = ProductRating
        fields = ["id", "user", "product", "value"]

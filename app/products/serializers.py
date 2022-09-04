from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Product, ProductRating


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "rating", "updated_at"]


class ProductRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "price"]


class ProductRatingSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if data["value"] < 0 or data["value"] > 5:
            raise serializers.ValidationError(
                {"value": "must be between 0 and 5"})
        return data

    class Meta:
        model = ProductRating
        fields = ["id", "user_id", "product_id", "value"]

        validators = [
            UniqueTogetherValidator(
                queryset=ProductRating.objects.all(),
                fields=['user_id', 'product_id'],
                message="user already rated this product"
            )
        ]


class ProductRatingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = ["value"]


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('username', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(validated_data['username'])
        user.set_password(password)
        user.save()
        return user

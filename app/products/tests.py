from datetime import datetime
from multiprocessing import AuthenticationError
from telnetlib import AUTHENTICATION

from django.contrib.auth.models import User
from django.test import Client, TestCase

from .models import Product, ProductRating
from .serializers import (CreateUserSerializer, ProductRatingSerializer,
                          ProductRequestSerializer, ProductSerializer)


class ProductTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        p1 = Product.objects.create(name="Initial product 1", price=50.50)
        p2 = Product.objects.create(name="Initial product 2", price=100)

        u1 = User.objects.create(username="user1", password="user1pw")
        u2 = User.objects.create(username="user2", password="user2pw")

        pr1 = ProductRating.objects.create(user_id=u1, product_id=p1, value=3)

    def test_product_insertion(self):
        t1 = datetime.now().isoformat()
        product = Product.objects.create(name="Product 1", price=12.50)
        t2 = datetime.now().isoformat()

        self.assertEqual(product.name, "Product 1")
        self.assertAlmostEqual(float(product.price), 12.5)
        self.assertEqual(product.rating, 0)
        self.assertGreaterEqual(product.updated_at.isoformat(), t1)
        self.assertLessEqual(product.updated_at.isoformat(), t2)

    def test_product_serializer_insertion(self):
        product_data = {
            "name": "Product 2",
            "price": 20.33,
            "rating": 5,
            "updated_at": "2000-01-01T12:00:00.000000"
        }
        serializer = ProductRequestSerializer(data=product_data)
        self.assertTrue(serializer.is_valid())
        t1 = datetime.now().isoformat()
        product = serializer.save()
        t2 = datetime.now().isoformat()
        self.assertEqual(product.name, "Product 2")
        self.assertAlmostEqual(float(product.price), 20.33)
        self.assertEqual(product.rating, 0)
        self.assertGreaterEqual(product.updated_at.isoformat(), t1)
        self.assertLessEqual(product.updated_at.isoformat(), t2)

    def test_product_same_name(self):
        product_same_name = {
            "name": "Initial product 1",
            "price": 1
        }
        serializer = ProductRequestSerializer(data=product_same_name)
        self.assertFalse(serializer.is_valid())

    def test_product_invalid_data(self):
        invalid_data = {
            "text": "test text",
            "description": "useless description"
        }
        serializer = ProductRequestSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_rating_product(self):
        user1 = User.objects.get(username="user1")
        product2 = Product.objects.get(name="Initial product 2")

        rating_data = {
            "user_id": user1.id,
            "product_id": product2.id,
            "value": 4,
        }
        serializer = ProductRatingSerializer(data=rating_data)
        self.assertTrue(serializer.is_valid())

    def test_rating_value_too_big(self):
        user2 = User.objects.get(username="user2")
        product2 = Product.objects.get(name="Initial product 2")
        rating_value_too_big = {
            "user_id": user2.id,
            "product_id": product2.id,
            "value": 6
        }
        serializer = ProductRatingSerializer(data=rating_value_too_big)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["value"][0], "must be between 0 and 5")

    def test_rating_value_too_small(self):
        user2 = User.objects.get(username="user2")
        product2 = Product.objects.get(name="Initial product 2")
        rating_value_too_small = {
            "user_id": user2.id,
            "product_id": product2.id,
            "value": -1
        }
        serializer = ProductRatingSerializer(data=rating_value_too_small)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["value"][0], "must be between 0 and 5")

    def test_rating_same_user(self):
        user1 = User.objects.get(username="user1")
        product1 = Product.objects.get(name="Initial product 1")
        rating_same_user = {
            "user_id": user1.id,
            "product_id": product1.id,
            "value": 3,
        }
        serializer = ProductRatingSerializer(data=rating_same_user)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["non_field_errors"][0], "user already rated this product")


class ApiTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_serializer = CreateUserSerializer(data={
            "username": "user1",
            "password": "user1pw"
        })
        if user_serializer.is_valid():
            u1 = user_serializer.save()
        else:
            raise Exception("Could not create user1")

        user_serializer = CreateUserSerializer(data={
            "username": "user2",
            "password": "user2pw"
        })
        if user_serializer.is_valid():
            u2 = user_serializer.save()
        else:
            raise Exception("Could not create user2")

        client = Client()
        response = client.post(
            "/products/",
            {"name": "Product 1", "price": 15.25}
        )
        p1 = response.json()
        response = client.post(
            "/products/",
            {"name": "Product 2", "price": 405}
        )

        response = client.post(
            "/login/",
            {"username": "user1", "password": "user1pw"}
        )
        token = response.json()["token"]

        r = client.post(
            "/products/{}/rate-product/".format(p1["id"]),
            {"value": 3},
            **{"HTTP_AUTHORIZATION": "Token {}".format(token)}
        )

    def setUp(self):
        self.client = Client()
        response = self.client.post(
            "/login/",
            {"username": "user1", "password": "user1pw"}
        )
        self.token1 = response.json()["token"]
        response = self.client.post(
            "/login/",
            {"username": "user2", "password": "user2pw"}
        )
        self.token2 = response.json()["token"]

    def test_list_products(self):
        response = self.client.get(
            "/products/",
            {"per_page": 1, "page": 2, "order_by": "rating", "order": "asc"}
        )
        products = response.json()["products"]
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["name"], "Product 1")

    def test_retreive_product(self):
        product = Product.objects.get(name="Product 1")
        response = self.client.get("/products/{}/".format(product.id))
        self.assertDictEqual(response.json(), ProductSerializer(product).data)

    def test_update_product(self):
        product = Product.objects.get(name="Product 2")
        response = self.client.put(
            "/products/{}/".format(product.id),
            {"name": "Product new name", "price": 99.99},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        updated_product = Product.objects.get(pk=product.id)
        self.assertEqual(updated_product.name, "Product new name")
        self.assertAlmostEqual(float(updated_product.price), 99.99)

    def test_delete_product(self):
        product = Product.objects.get(name="Product 2")
        response = self.client.delete("/products/{}/".format(product.id))
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/products/{}/".format(product.id))
        self.assertEqual(response.status_code, 404)

    def test_user_password_hashed(self):
        user = User.objects.get(username="user1")
        self.assertNotEqual(user.password, "user1pw")

    def test_product_rating(self):
        product = Product.objects.get(name="Product 1")
        self.assertAlmostEqual(product.rating, 3)

    def test_update_product_rating(self):
        product = Product.objects.get(name="Product 1")

        response = self.client.post(
            "/products/{}/rate-product/".format(product.id),
            {"value": 4},
            **{"HTTP_AUTHORIZATION": "Token {}".format(self.token2)}
        )
        self.assertAlmostEqual(response.json()["rating"], 3.5)

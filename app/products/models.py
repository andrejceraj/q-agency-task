from itertools import product
from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=200, null=False, unique=True)
    price = models.DecimalField(null=False, decimal_places=2, max_digits=12)
    rating = models.FloatField(null=False, default=0)
    updated_at = models.DateTimeField(null=False, auto_now_add=True)

    def __str__(self):
        return self.name

    def _search_value(self):
        return "{} {} {}".format(self.name, self.price, round(self.rating, 3))


class ProductRating(models.Model):
    user_id = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    product_id = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(null=False)

    def __str__(self):
        return "{} rated {} with {} stars".format(self.user_id, self.product_id, self.value)

    class Meta:
        unique_together = ('user_id', 'product_id',)

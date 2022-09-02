from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=200, null=False, unique=True)
    price = models.DecimalField(null=False, decimal_places=2, max_digits=12)
    rating = models.FloatField(null=False, default=0)
    updated_at = models.DateTimeField(null=False)

    def __str__(self):
        return self.name


class ProductRating(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(null=False)

    def __str__(self):
        return "{} rated {} with {} stars".format(self.user, self.product, self.value)

    class Meta:
        unique_together = ('user', 'product',)

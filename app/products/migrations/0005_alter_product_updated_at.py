# Generated by Django 4.1 on 2022-09-06 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_rename_product_productrating_product_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='updated_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
# Generated by Django 4.1 on 2022-10-17 14:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0007_coupon_product_offer_price_product_percentage_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coupon",
            name="discount",
            field=models.FloatField(
                verbose_name=[
                    django.core.validators.MaxValueValidator(500),
                    django.core.validators.MinValueValidator(1),
                ]
            ),
        ),
    ]
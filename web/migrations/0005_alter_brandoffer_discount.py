# Generated by Django 4.1 on 2022-10-17 14:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0004_productoffer_categoryoffer_brandoffer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="brandoffer",
            name="discount",
            field=models.IntegerField(
                validators=[
                    django.core.validators.MaxValueValidator(50),
                    django.core.validators.MinValueValidator(1),
                ]
            ),
        ),
    ]

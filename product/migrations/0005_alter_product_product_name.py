# Generated by Django 4.1 on 2022-10-01 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0004_alter_product_product_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="product_name",
            field=models.CharField(max_length=500, unique=True),
        ),
    ]

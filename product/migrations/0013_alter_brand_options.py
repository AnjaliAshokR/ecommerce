# Generated by Django 4.1 on 2022-10-20 17:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0012_wishlist"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="brand",
            options={"verbose_name": "brand", "verbose_name_plural": "brands"},
        ),
    ]

# Generated by Django 4.1 on 2022-09-30 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="payment_id",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
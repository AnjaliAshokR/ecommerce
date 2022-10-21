from django.db import models
from account.models import Account
from product.models import Product, Variation, Category, Brand
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

STATUS1 = (
    ("New", "New"),
    ("Accepted", "Accepted"),
    ("Completed", "Completed"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
    ("Returned", "Returned"),
    ("Waiting for return", "Waiting for return"),
    ("Cancelled", "Cancelled"),
)


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ("New", "New"),
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
        ("Shipped", "Shipped"),
        ("Returned", "Returned"),
        ("Waiting for return", "Waiting for return"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS, default="New")
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    return_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    return_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name


class BrandOffer(models.Model):
    brand_name = models.OneToOneField(Brand, on_delete=models.CASCADE)
    discount = models.IntegerField(
        validators=[MaxValueValidator(50), MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=True)

    def __int__(self):
        return self.brand_name


class CategoryOffer(models.Model):
    category_name = models.OneToOneField(Category, on_delete=models.CASCADE)
    discount = models.IntegerField(
        validators=[MaxValueValidator(50), MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=True)

    def __int__(self):
        return self.category_name


class ProductOffer(models.Model):
    product_name = models.OneToOneField(Product, on_delete=models.CASCADE)
    discount = models.IntegerField(
        validators=[MaxValueValidator(50), MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=True)

    def __int__(self):
        return self.product_name

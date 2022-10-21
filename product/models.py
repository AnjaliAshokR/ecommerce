from django.db import models
from django.urls import reverse
from account.models import Account
from django.utils import timezone
from django.db.models import Sum
from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import CheckConstraint, Q

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to="photos/categories/", default="")

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def get_url(self):
        return reverse("products_by_category", args=[self.slug])

    def __str__(self):
        return self.category_name


class Brand(models.Model):
    brand_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    brand_logo = models.ImageField(upload_to="photos/brands")

    class Meta:
        verbose_name = "brand"
        verbose_name_plural = "brands"

    def get_url_brand(self):
        return reverse("products_by_brand", args=[self.slug])

    def __str__(self):
        return self.brand_name


class Product(models.Model):
    product_name = models.CharField(max_length=500, unique=True)
    product_code = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(max_length=500, blank=True)
    offer_price = models.IntegerField(default=0)
    percentage = models.IntegerField(default=0)
    details = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    featured = models.BooleanField(default=False)
    images = models.ImageField(upload_to="photos/products")
    images1 = models.ImageField(upload_to="photos/products")
    images2 = models.ImageField(upload_to="photos/products")
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_date = models.DateTimeField(auto_now=True)
    color = models.CharField(max_length=100, blank=True)
    material = models.CharField(max_length=100, blank=True)
    occasion = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=100, blank=True)
    pattern = models.CharField(max_length=100, blank=True)
    country_of_origin = models.CharField(max_length=100, blank=True)
    Manufacture = models.TextField(max_length=500, blank=True)

    def get_url(self):
        return reverse("product_detail", args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def Offer_Price(self):
        try:
            if self.productoffer.is_valid:
                offer_price = (self.price * self.productoffer.discount) / 100
                new_price = self.price - offer_price
                return {
                    "new_price": new_price,
                    "discount": self.productoffer.discount,
                }
            raise
        except:
            try:
                if self.brand.brandoffer.is_valid:
                    offer_price = (self.price * self.brand.brandoffer.discount) / 100
                    new_price = self.price - offer_price
                    print(offer_price)
                    return {
                        "new_price": new_price,
                        "discount": self.brand.brandoffer.discount,
                    }
                raise
            except:
                try:
                    if self.category.categoryoffer.is_valid:
                        offer_price = (
                            self.price * self.category.categoryoffer.discount
                        ) / 100
                        new_price = self.price - offer_price
                        return {
                            "new_price": new_price,
                            "discount": self.category.categoryoffer.discount,
                        }
                    raise
                except:
                    pass

    def get_count(self, month=timezone.now().month):
        orderproduct = apps.get_model("web", "OrderProduct")
        order = orderproduct.objects.filter(product=self, created_at__month=month)
        return order.values("product").annotate(quantity=Sum("quantity"))

    def get_revenue(self, month=timezone.now().month):
        orderproduct = apps.get_model("web", "OrderProduct")
        orders = orderproduct.objects.filter(product=self, created_at__month=month)
        return orders.values("product").annotate(revenue=Sum("product_price"))

    def get_profit(self, month=timezone.now().month):
        orderproduct = apps.get_model("web", "OrderProduct")
        orders = orderproduct.objects.filter(product=self, created_at__month=month)
        profit_calculted = orders.values("product").annotate(
            profit=Sum("product_price")
        )
        profit_calculated = profit_calculted[0]["profit"] * 0.23
        return profit_calculated


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(
            variation_category="color", is_active=True
        )

    def sizes(self):
        return super(VariationManager, self).filter(
            variation_category="size", is_active=True
        )


variation_category_choice = (
    ("color", "color"),
    ("size", "size"),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=100, choices=variation_category_choice
    )
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        if self.product.offer_price == 0:
            return self.product.price * self.quantity
        else:
            return self.product.offer_price * self.quantity

    def __unicode__(self):
        return self.product


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="store/products", max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = "productgallery"
        verbose_name_plural = "productgallery"


min = 1.0
max = 500.0


class Coupon(models.Model):
    coupon_code = models.CharField(max_length=10, blank=True)
    discount = models.FloatField(
        validators=[MinValueValidator(min), MaxValueValidator(max)],
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.coupon_code


class UsedCoupon(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True)


class Wishlist(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Wishlist"

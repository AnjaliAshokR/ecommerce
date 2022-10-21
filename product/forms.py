from django import forms
from .models import Product, Category, Brand, UsedCoupon, Coupon
from django.core.validators import MaxValueValidator, MinValueValidator


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "product_name",
            "product_code",
            "created_by",
            "color",
            "material",
            "occasion",
            "type",
            "pattern",
            "country_of_origin",
            "Manufacture",
            "slug",
            "description",
            "details",
            "price",
            "images",
            "images1",
            "images2",
            "is_available",
            "featured",
            "stock",
            "category",
            "brand",
        )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("category_name", "slug", "description", "cat_image")


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ("brand_name", "slug", "brand_logo")


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ("coupon_code", "discount", "is_active")


class UsedCouponForm(forms.ModelForm):
    class Meta:
        model = UsedCoupon
        fields = ("user", "coupon")

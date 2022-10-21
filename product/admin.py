from django.contrib import admin
from . import models
from .models import (
    Product,
    Brand,
    Category,
    Cart,
    CartItem,
    Variation,
    Coupon,
    UsedCoupon,
    Wishlist,
)


# Register your models here.


class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "brand_name",
        "slug",
    )
    prepopulated_fields = {"slug": ("brand_name",)}


admin.site.register(Brand, BrandAdmin)


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("category_name",)}
    list_display = ("category_name", "slug")


admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "price",
        "stock",
        "category",
        "modified_date",
        "is_available",
    )
    prepopulated_fields = {"slug": ("product_name",)}


admin.site.register(Product, ProductAdmin)


class CartAdmin(admin.ModelAdmin):
    list_display = ("cart_id", "date_added")


class CartItemAdmin(admin.ModelAdmin):
    list_display = ("product", "cart", "quantity")


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)


class VariationAdmin(admin.ModelAdmin):
    list_display = ("product", "variation_category", "variation_value", "is_active")
    list_editable = ("is_active",)
    list_filter = ("product", "variation_category", "variation_value", "is_active")


admin.site.register(Variation, VariationAdmin)


class CouponAdmin(admin.ModelAdmin):
    list_display = ("coupon_code", "discount", "is_active")


class UsedCouponAdmin(admin.ModelAdmin):
    list_display = ("user", "coupon")


class WishAdmin(admin.ModelAdmin):
    list_display = ("user", "product")


admin.site.register(Wishlist, WishAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(UsedCoupon, UsedCouponAdmin)

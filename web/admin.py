from django.contrib import admin
from .models import (
    Payment,
    Order,
    OrderProduct,
    BrandOffer,
    CategoryOffer,
    ProductOffer,
)

# Register your models here.

admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(BrandOffer)
admin.site.register(CategoryOffer)
admin.site.register(ProductOffer)

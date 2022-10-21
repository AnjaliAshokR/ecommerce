from django.urls import path, include

from admin_stylaza import views

urlpatterns = [
    path("", views.admin_login, name="admin-login"),
    path("admin-home/", views.admin_home, name="admin-home"),
    path("admin-logout/", views.admin_logout, name="admin-logout"),
    path("admin-category", views.category_list, name="category-list"),
    path("admin-brand", views.brand_list, name="brand-list"),
    path("admin-product", views.product_list, name="product-list"),
    path("add-admin-category", views.add_category, name="add-category"),
    path("add-admin-brand", views.add_brand, name="add-brand"),
    path("add-admin-product", views.add_product, name="add-product"),
    path("delete-category/<int:id>", views.delete_category, name="delete-category"),
    path("delete-brand/<int:id>", views.delete_brand, name="delete-brand"),
    path("delete-product/<int:id>", views.delete_product, name="delete-product"),
    path("edit-product/<int:id>", views.edit_product, name="edit-product"),
    path("edit-category/<int:id>", views.edit_category, name="edit-category"),
    path("edit-brand/<int:id>", views.edit_brand, name="edit-brand"),
    # user management
    path("admin-user", views.user_list, name="user-list"),
    path("block-user/<int:id>", views.block_user, name="block-user"),
    path("unblock-user/<int:id>", views.unblock_user, name="unblock-user"),
    # order management
    path("order-display/", views.order_display, name="order-display"),
    path(
        "order-details-admin/<int:id>/",
        views.order_details_admin,
        name="order-details-admin",
    ),
    path("order-status/<int:id>/", views.order_status, name="order-status"),
    # coupon management
    path("view-coupon", views.view_coupon, name="view-coupon"),
    path("add-admin-coupon", views.add_coupon, name="add-coupon"),
    path("delete-coupon/<int:id>", views.delete_coupon, name="delete-coupon"),
    # brand management
    path("brand-offer", views.brand_offer, name="brand-offer"),
    path("add-brand-offer", views.add_brand_offer, name="add-brand-offer"),
    path(
        "delete-brand-offer/<brand_id>",
        views.delete_brand_offer,
        name="delete-brand-offer",
    ),
    path(
        "edit-brand-offer/<brand_id>", views.edit_brand_offer, name="edit-brand-offer"
    ),
    path(
        "block-brand-offer/<brand_id>",
        views.block_brand_offer,
        name="block-brand-offer",
    ),
    path(
        "unblock-brand-offer/<brand_id>",
        views.unblock_brand_offer,
        name="unblock-brand-offer",
    ),
    # category management
    path("category-offer", views.category_offer, name="category-offer"),
    path("add-category-offer", views.add_category_offer, name="add-category-offer"),
    path(
        "delete-category-offer/<category_id>",
        views.delete_category_offer,
        name="delete-category-offer",
    ),
    path(
        "edit-category-offer/<category_id>",
        views.edit_category_offer,
        name="edit-category-offer",
    ),
    path(
        "block-category-offer/<category_id>",
        views.block_category_offer,
        name="block-category-offer",
    ),
    path(
        "unblock-category-offer/<category_id>",
        views.unblock_category_offer,
        name="unblock-category-offer",
    ),
    # product management
    path("product-offer", views.product_offer, name="product-offer"),
    path("add-product-offer", views.add_product_offer, name="add-product-offer"),
    path(
        "delete-product-offer/<product_id>",
        views.delete_product_offer,
        name="delete-product-offer",
    ),
    path(
        "edit-product-offer/<product_id>",
        views.edit_product_offer,
        name="edit-product-offer",
    ),
    path(
        "block-product-offer/<product_id>",
        views.block_product_offer,
        name="block-product-offer",
    ),
    path(
        "unblock-product-offer/<product_id>",
        views.unblock_product_offer,
        name="unblock-product-offer",
    ),
    # sales Report
    path("sales-report", views.sales_report, name="sales-report"),
    path("sales-export-csv", views.sales_export_csv, name="sales-export-csv"),
    path("sales-export-pdf", views.sales_export_pdf, name="sales-export-pdf"),
    path("status-search/<status>", views.status_search, name="status-search"),
    path(
        "admin-order-detail/<int:order_id>/",
        views.order_details,
        name="admin-order-detail",
    ),
]

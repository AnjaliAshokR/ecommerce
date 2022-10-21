from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from account.models import Account
from django.db.models import Q
from django.views.decorators.cache import cache_control
from product.models import Product, Category, Brand, Coupon
from product.forms import (
    ProductForm,
    BrandForm,
    CategoryForm,
    UsedCouponForm,
    CouponForm,
)
from web.models import (
    Order,
    OrderProduct,
    Payment,
    STATUS1,
    CategoryOffer,
    BrandOffer,
    ProductOffer,
)
from web.forms import StatusForm, CategoryOfferForm, ProductOfferForm, BrandOfferForm
from django.db.models import Q, Count
from django.db.models.functions import ExtractMonth
import calendar
import csv
from admin_stylaza.pdf import html_to_pdf
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import render_to_string

# Create your views here.


# login view function


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect("admin-home/")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None and user.is_superadmin:
            auth.login(request, user)
            messages.success(request, "Welcome Admin! You are successfully logged in")
            return redirect(admin_home)
        else:
            messages.error(request, "invalid credential")
            return redirect(admin_login)

    return render(request, "admin/admin_login.html")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_home(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        New = 0
        Completed = 0
        Cancelled = 0
        Shipped = 0
        Returned = 0
        Delivered = 0
        waiting = 0
        income = 0
        orders = Order.objects.filter(is_ordered=True)
        for order in orders:
            income += order.order_total
        income = int(income)
        labels = []
        data = []
        orders = (
            OrderProduct.objects.annotate(month=ExtractMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .values("month", "count")
        )

        labels = [
            "jan",
            "feb",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
        ]
        data = [0, 0, 0, 0, 0, 0, 0]
        for d in orders:
            labels.append(calendar.month_name[d["month"]])
            data.append([d["count"]])
        labels1 = []
        data1 = []

        queryset = Order.objects.all()
        for i in queryset:
            if i.status == "New":
                New = New + 1
            elif i.status == "Completed":
                Completed += 1
            elif i.status == "Cancelled":
                Cancelled += 1
            elif i.status == "Shipped":
                Shipped += 1
            elif i.status == "Returned":
                Returned += 1
            elif i.status == "Delivered":
                Delivered += 1
            elif i.status == "Waiting for return":
                waiting += 1

        labels1 = [
            "New",
            "Canceled",
            "Completed",
            "Shipped",
            "Returned",
            "Delivered",
            "Waiting for return",
        ]
        data1 = [New, Returned, Cancelled, Completed, Shipped, Delivered, waiting]
        print(data1)
        order_count = Order.objects.count()
        product_count = Product.objects.count()

        cat_count = Category.objects.count()
        user_count = Account.objects.count()

        category = Category.objects.all().order_by("-id")
        products = Product.objects.all().order_by("-id")
        orderproducts = OrderProduct.objects.all().order_by("-id")

        context = {
            "cat_count": cat_count,
            "product_count": product_count,
            "order_count": order_count,
            "labels1": labels1,
            "data1": data1,
            "data": data,
            "category": category,
            "products": products,
            "orderproducts": orderproducts,
            "income": income,
            "user_count": user_count,
        }
        return render(request, "admin/admin_home.html", context)
    else:
        redirect("/")


@login_required(login_url="/")
def admin_logout(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        request.session.flush()
        auth.logout(request)
        messages.warning(request, "You are logged out")
        return redirect(admin_login)
    else:
        redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category_list(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        search_key = (
            request.GET.get("key") if request.GET.get("key") is not None else ""
        )
        values = Category.objects.all().order_by("id") and Category.objects.filter(
            Q(category_name__icontains=search_key)
            | Q(description__icontains=search_key)
        )
        return render(request, "admin/categorylist.html", {"values": values})
    else:
        redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def brand_list(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        search_key = (
            request.GET.get("key") if request.GET.get("key") is not None else ""
        )
        brands = Brand.objects.all().order_by("id") and Brand.objects.filter(
            Q(brand_name__icontains=search_key)
        )
        return render(request, "admin/brandlist.html", {"brands": brands})
    else:
        redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_list(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        search_key = (
            request.GET.get("key") if request.GET.get("key") is not None else ""
        )
        products = Product.objects.all().order_by("id") and Product.objects.filter(
            Q(product_name__icontains=search_key) | Q(description__icontains=search_key)
        )
        return render(request, "admin/productlist.html", {"products": products})
    else:
        redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_category(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        if request.method == "POST":
            cat_form = CategoryForm(request.POST, request.FILES)
            if cat_form.is_valid():
                cat_form.save()
                messages.success(request, "Your category has been added sucessfully")
            else:
                messages.error(request, "Error")

            return redirect(category_list)
        cat_form = CategoryForm()
        cats = Category.objects.all()
        context = {"cat_form": cat_form, "cats": cats}
        return render(request, "admin/addcategory.html", context)
    else:
        redirect("/")


@login_required(login_url="/")
def delete_category(request, id):
    if request.user.is_authenticated and request.user.is_superadmin:
        my_cat = Category.objects.get(id=id)
        my_cat.delete()
        return redirect(category_list)
    else:
        redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_brand(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        if request.method == "POST":
            brand_form = BrandForm(request.POST, request.FILES)
            if brand_form.is_valid():
                brand_form.save()
                messages.success(request, "Your brand has been added sucessfully")
            else:
                messages.error(request, "Error")

            return redirect(brand_list)
        brand_form = BrandForm()
        brands = Brand.objects.all()
        context = {"brand_form": brand_form, "brands": brands}
        return render(request, "admin/addbrand.html", context)
    else:
        redirect("/")


@login_required(login_url="/")
def delete_brand(request, id):
    if request.user.is_authenticated and request.user.is_superadmin:
        my_brand = Brand.objects.get(id=id)
        my_brand.delete()
        messages.warning(request, "Brand has been deleted")
        return redirect(brand_list)
    else:
        redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_product(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        if request.method == "POST":
            prod_form = ProductForm(request.POST, request.FILES)
            if prod_form.is_valid():
                prod_form.save()
                messages.success(request, "Your product has been added successfully")
            else:
                messages.error(request, "Error")

            return redirect(product_list)
        prod_form = ProductForm()

        context = {"prod_form": prod_form}
        return render(request, "admin/addproduct.html", context)
    else:
        redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_product(request, id):
    if request.user.is_authenticated and request.user.is_superadmin:
        product = Product.objects.get(id=id)
        form = ProductForm(instance=product)
        if request.method == "POST":
            form = ProductForm(request.POST, request.FILES, instance=product)

            if form.is_valid():
                form.save()
                messages.success(request, "Product has been edited successfully")
                return redirect(product_list)
        else:

            return render(request, "admin/productedit.html", {"form": form})
    else:
        redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_category(request, id):
    if request.user.is_authenticated and request.user.is_superadmin:
        category = Category.objects.get(id=id)
        form = CategoryForm(instance=category)
        if request.method == "POST":
            form = CategoryForm(request.POST, request.FILES, instance=category)

            if form.is_valid():
                form.save()
                messages.success(request, "Category has been edited successfully")
                return redirect(category_list)
        else:

            return render(request, "admin/categoryedit.html", {"form": form})
    else:
        redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_brand(request, id):
    if request.user.is_authenticated and request.user.is_superadmin:
        brand = Brand.objects.get(id=id)
        form = BrandForm(instance=brand)
        if request.method == "POST":
            form = BrandForm(request.POST, request.FILES, instance=brand)

            if form.is_valid():
                form.save()
                messages.success(request, "Brand has been edited successfully")
                return redirect(brand_list)
        else:

            return render(request, "admin/brandedit.html", {"form": form})
    else:
        redirect("/")


@login_required(login_url="/")
def delete_product(request, id):
    if request.user.is_authenticated and request.user.is_superadmin:
        my_product = Product.objects.get(id=id)
        my_product.delete()
        messages.warning(request, "Product has been deleted")
        return redirect(product_list)
    else:
        redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_list(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        search_key = (
            request.GET.get("key") if request.GET.get("key") is not None else ""
        )
        users = Account.objects.order_by("id").filter(
            is_admin=False
        ).all() and Account.objects.filter(username__istartswith=search_key)
        return render(request, "admin/userlist.html", {"users": users})
    else:
        redirect("/")


@login_required(login_url="/")
def block_user(request, id):
    if request.user.is_authenticated and request.user.is_superadmin:
        user_instance = Account.objects.get(id=id)
        user_instance.is_active = False
        user_instance.is_blocked = True
        user_instance.save()
        messages.success(request, "user is successfully blocked")
        return redirect(user_list)
    else:
        redirect("/")


@login_required(login_url="/")
def unblock_user(request, id):
    if request.user.is_authenticated and request.user.is_superadmin:
        user_instance = Account.objects.get(id=id)
        user_instance.is_active = True
        user_instance.is_blocked = False
        user_instance.save()
        messages.success(request, "user is successfully unblocked")
        return redirect(user_list)
    else:
        redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_display(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        choices = STATUS1
        if "key" in request.GET:
            search_key = (
                request.GET.get("key") if request.GET.get("key") is not None else ""
            )
            orders = (
                Order.objects.filter(order_number__istartswith=search_key).order_by(
                    "id"
                )
                or Order.objects.filter(first_name=search_key).order_by("id")
                or Order.objects.filter(last_name=search_key).order_by("id")
            )
            context = {
                "orders": orders,
                "status": STATUS1,
            }
            return render(request, "admin/orderadmin.html", context)
        else:
            orders = Order.objects.filter() or Order.objects.filter(is_ordered=False)
            order_products = OrderProduct.objects.all().order_by("-id")
            payment = Payment.objects.all()

            context = {
                "orders": orders,
                "order_products": order_products,
                "payment": payment,
                "status": STATUS1,
            }

            return render(request, "admin/orderadmin.html", context)

    else:
        return redirect("/")


def status_search(request, status):
    if request.user.is_authenticated and request.user.is_superadmin:
        # status = request.POST.get("statuses")
        orders = Order.objects.order_by("id").filter(
            is_ordered=True
        ).all() and Order.objects.filter(status=status)
        context = {
            "orders": orders,
            "status": STATUS1,
        }
        return render(request, "admin/orderadmin.html", context)
    else:
        return redirect("/")


@login_required(login_url="/")
def order_details_admin(request, id):
    if request.user.is_authenticated and request.user.is_superadmin:
        order_products = OrderProduct.objects.filter(order=id).order_by("-id")
        order_statuses = OrderProduct
        return render(
            request, "admin/orderdetailsadmin.html", {"order_products": order_products}
        )

    else:
        return redirect("/")


@login_required(login_url="/")
def order_status(request, id):
    if request.user.is_authenticated and request.user.is_superadmin:
        status = request.POST.get("status")
        order = Order.objects.get(order_number=id)

        if order.status == "Cancelled" or order.status == "Returned":
            return redirect(order_display)
        else:
            if status == "Cancelled":
                order_products = OrderProduct.objects.filter(order__order_number=id)
                order.status = status
                order.is_ordered = False
                order.payment.status = "REFUNDED"
                order.payment.save()
                order.save()

                for order_product in order_products:
                    order_product.ordered = False
                    order_product.product.stock += order_product.quantity
                    order_product.product.save()
            elif status == "Returned":
                order_products = OrderProduct.objects.filter(order__order_number=id)
                order.status = status
                order.is_ordered = False
                order.payment.status = "REFUNDED"
                order.payment.save()
                order.save()

                for order_product in order_products:
                    order_product.ordered = False
                    order_product.product.stock += order_product.quantity
                    order_product.product.save()
            elif status == "Delivered":
                order.status = status
                order.payment.status = "Payment Complete"
                order.payment.save()
                order.save()
            elif status == "Complete":
                order.status = status
                order.payment.status = "Payment Complete"
                order.payment.save()
                order.save()

            else:
                order.status = status
                order.save()
        return redirect(order_display)
    else:
        return redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_coupon(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        values = Coupon.objects.all()
        return render(request, "admin/couponlist.html", {"values": values})
    else:
        return redirect("/")


@login_required(login_url="/")
def delete_coupon(request, id):
    if request.user.is_authenticated and request.user.is_superadmin:
        my_coupon = Coupon.objects.get(id=id)
        my_coupon.delete()
        return redirect(view_coupon)
    else:
        return redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_coupon(request):
    if request.user.is_authenticated and request.user.is_superadmin:

        if request.method == "POST":
            coupon_form = CouponForm(request.POST, request.FILES)
            if coupon_form.is_valid():
                coupon_form.save()
                messages.success(request, "Your coupon has been added sucessfully")
            else:
                messages.error(request, "Error")

            return redirect(view_coupon)
        coupon_form = CouponForm()

        context = {"coupon_form": coupon_form}
        return render(request, "admin/addcoupon.html", context)
    else:
        return redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def brand_offer(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        offers = BrandOffer.objects.order_by("id").all()
        return render(request, "admin/existing_brand_Offer.html", {"offers": offers})
    else:
        return redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_brand_offer(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        form = BrandOfferForm()
        if request.method == "POST":
            form = BrandOfferForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("brand-offer")
        context = {"form": form}
        return render(request, "admin/add_brand_offer.html", context)
    else:
        return redirect("/")


@login_required(login_url="/")
def edit_brand_offer(request, brand_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        brand_offers = BrandOffer.objects.get(pk=brand_id)
        form = BrandOfferForm(instance=brand_offers)
        if request.method == "POST":
            form = BrandOfferForm(request.POST, instance=brand_offers)
            if form.is_valid():
                try:
                    form.save()

                except:
                    context = {"form": form}
                    return render(request, "admin/editBrandOffer.html", context)
                return redirect("brand-offer")
        context = {"form": form}
        return render(request, "admin/editBrandOffer.html", context)
    else:
        return redirect("/")


@login_required(login_url="/")
def delete_brand_offer(request, brand_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        brand = BrandOffer.objects.get(pk=brand_id)
        brand.delete()
        return redirect("brand-offer")
    else:
        return redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category_offer(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        offers = CategoryOffer.objects.order_by("id").all()
        return render(request, "admin/existing_category_Offer.html", {"offers": offers})
    else:
        return redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_category_offer(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        form = CategoryOfferForm()
        if request.method == "POST":
            form = CategoryOfferForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("category-offer")
        context = {"form": form}
        return render(request, "admin/add_category_offer.html", context)
    else:
        return redirect("/")


@login_required(login_url="/")
def delete_category_offer(request, category_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        category = CategoryOffer.objects.get(pk=category_id)
        category.delete()
        messages.warning(request, "Category has been added deleted")
        return redirect("category-offer")
    else:
        return redirect("/")


@login_required(login_url="/")
def edit_category_offer(request, category_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        categories = CategoryOffer.objects.get(pk=category_id)
        form = CategoryOfferForm(instance=categories)
        if request.method == "POST":
            form = CategoryOfferForm(request.POST, instance=categories)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, "Brand has been edited")

                except:
                    context = {"form": form}
                    messages.error(request, "Error")
                    return render(request, "admin/editCategoryOffer.html", context)
                return redirect("category-offer")

        context = {"form": form}
        return render(request, "admin/editCategoryOffer.html", context)
    else:
        return redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_offer(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        offers = ProductOffer.objects.order_by("id").all()
        return render(request, "admin/existing_product_Offer.html", {"offers": offers})
    else:
        return redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_product_offer(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        form = ProductOfferForm()
        if request.method == "POST":
            form = ProductOfferForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("product-offer")
        context = {"form": form}
        return render(request, "admin/add_product_offer.html", context)
    else:
        return redirect("/")


@login_required(login_url="/")
def edit_product_offer(request, product_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        products = ProductOffer.objects.get(pk=product_id)
        form = ProductOfferForm(instance=products)
        if request.method == "POST":
            form = ProductOfferForm(request.POST, instance=products)
            if form.is_valid():
                try:
                    form.save()

                except:
                    context = {"form": form}
                    return render(request, "admin/editProductOffer.html", context)
                return redirect("product-offer")

        context = {"form": form}
        return render(request, "admin/editProductOffer.html", context)
    else:
        return redirect("/")


@login_required(login_url="/")
def delete_product_offer(request, product_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        product = ProductOffer.objects.get(pk=product_id)
        product.delete()
        return redirect("product-offer")
    else:
        return redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_report(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        product = Product.objects.all()
        context = {"product": product}
        return render(request, "admin/salesreport.html", context)
    else:
        return redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_export_csv(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=products.csv"

        writer = csv.writer(response)
        products = Product.objects.all().order_by("-id")

        writer.writerow(
            [
                "Product",
                "Brand",
                "Category",
                "Stock",
                "Price",
                "Sales Count",
                "Revenue",
                "Profit",
            ]
        )

        for product in products:
            writer.writerow(
                [
                    product.product_name,
                    product.brand.brand_name,
                    product.category.category_name,
                    product.stock,
                    product.price,
                    product.get_count()[0]["quantity"],
                    product.get_revenue()[0]["revenue"],
                    product.get_profit(),
                ]
            )
        return response
    else:
        return redirect("/")


@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_export_pdf(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        product = Product.objects.all()
        open("templates/admin/pdf_out.html", "w", encoding="utf-8").write(
            render_to_string("admin/sales_export_pdf.html", {"product": product})
        )
        pdf = html_to_pdf("admin/pdf_out.html")
        return HttpResponse(pdf, content_type="application/pdf")
    else:
        return redirect("/")


@login_required(login_url="/")
def block_product_offer(request, product_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        product_offer = ProductOffer.objects.get(pk=product_id)
        product_offer.is_valid = False
        product_offer.save()
        return redirect("product-offer")
    else:
        return redirect("/")


@login_required(login_url="/")
def unblock_product_offer(request, product_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        product_offer = ProductOffer.objects.get(pk=product_id)
        product_offer.is_valid = True
        product_offer.save()
        return redirect("product-offer")
    else:
        return redirect("/")


@login_required(login_url="/")
def block_brand_offer(request, brand_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        brand_offer = BrandOffer.objects.get(pk=brand_id)
        brand_offer.is_valid = False
        brand_offer.save()
        return redirect("brand-offer")
    else:
        return redirect("/")


@login_required(login_url="/")
def unblock_brand_offer(request, brand_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        brand_offer = BrandOffer.objects.get(pk=brand_id)
        brand_offer.is_valid = True
        brand_offer.save()
        return redirect("brand-offer")
    else:
        return redirect("/")


@login_required(login_url="/")
def block_category_offer(request, category_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        category_offer = CategoryOffer.objects.get(pk=category_id)
        category_offer.is_valid = False
        category_offer.save()
        return redirect("category-offer")
    else:
        return redirect("/")


@login_required(login_url="/")
def unblock_category_offer(request, category_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        category_offer = CategoryOffer.objects.get(pk=category_id)
        category_offer.is_valid = True
        category_offer.save()
        return redirect("category-offer")
    else:
        return redirect("/")


def order_details(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        "order_detail": order_detail,
        "order": order,
        "subtotal": subtotal,
    }
    return render(request, "admin/order_detail.html", context)

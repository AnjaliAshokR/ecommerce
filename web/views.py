import json
from django.db.models import Q
import requests
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from product.models import Product, Category, Cart, CartItem, Coupon, UsedCoupon
from django.shortcuts import render, redirect
from .forms import RegistrationForm, OrderForm
import datetime
from .models import Order, Payment, OrderProduct
from account.models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from account.forms import UserForm, UserProfileForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import cache_control
from .otp_verify import sent_otp, check_otp
from product.models import (
    Product,
    Cart,
    CartItem,
    Variation,
    ProductGallery,
    Wishlist,
    Brand,
)
from product.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse

# Create your views here.


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            request.session["first_name"] = form.cleaned_data["first_name"]
            request.session["last_name"] = form.cleaned_data["last_name"]
            request.session["email"] = form.cleaned_data["email"]
            request.session["phone_number"] = form.cleaned_data["phone_number"]
            request.session["password"] = form.cleaned_data["password"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            username = email.split("@")[0]
            request.session["username"] = username

            sent_otp(phone_number)
            return redirect("confirm")
    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }
    return render(request, "stylaza/register.html", context)  # template needed


def confirm_signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        otp = request.POST["otp_code"]

        phone_number = request.session["phone_number"]

        if check_otp(phone_number, otp):
            first_name = request.session["first_name"]
            last_name = request.session["last_name"]
            email = request.session["email"]
            phone_number = request.session["phone_number"]
            password = request.session["password"]
            username = request.session["username"]

            usr = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                username=username,
            )
            usr.phone_number = phone_number
            usr.is_active = True
            usr.save()
            messages.success(request, "User have been successfully registered")
            return redirect("otp_user_login")  # redirect to login page
        else:

            return redirect("confirm_signup")  # redirect to otp page
    return render(request, "stylaza/otp_confirm.html")


def sign_in(request):

    if request.method == "POST":
        phone_number = request.POST["phone_number"]
        try:
            if Account.objects.filter(phone_number=phone_number).first():
                sent_otp(phone_number)
                request.session["phone_number"] = phone_number
                # __setitem__(phone_number, phone_number) # storing value temporarily in session
                return redirect("otp_check")  # reroute path not created
        except:
            messages.error(request, "User not registered")
            return redirect("otp_register")
    return render(request, "stylaza/otp.html", {})


def otp_check(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        otp = request.POST["otp_code"]
        mobile = request.session["phone_number"]
        if_valid = check_otp(mobile, otp)
        if if_valid:
            try:
                usr = Account.objects.get(phone_number=mobile)

                cart = Cart.objects.get(
                    cart_id=_cart_id(request)
                )  # this query will get or create a new cart
                if cart is not None:
                    print("cart is not empty ", cart)
                is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exist:
                    cart_item = CartItem.objects.filter(cart=cart)
                    for item in cart_item:
                        item.user = usr
                        item.save()
            except:
                pass
            usr = Account.objects.get(phone_number=mobile)
            auth.login(request, usr)
            messages.success(request, "Authenticated Successfully")
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split("=") for x in query.split("&"))
                if "next" in params:
                    nextPage = params["next"]
                    return redirect(nextPage)
            except:
                return redirect("home")

        else:
            messages.error(request, "OTP not Valid")
            return redirect("otp_check")

    return render(request, "stylaza/otp_confirm.html", {})


def resent_otp(request):
    mobile = request.session["phone_number"]
    sent_otp(mobile)
    return redirect("otp_check")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    if request.user.is_authenticated:
        return redirect("/")

    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        usr = auth.authenticate(email=email, password=password)
        if usr is not None:
            try:

                cart = Cart.objects.get(cart_id=_cart_id(request))
                if cart is not None:
                    print("cart is not empty ", cart)
                is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exist:

                    cart_item = CartItem.objects.filter(cart=cart)

                    for item in cart_item:
                        item.user = usr
                        item.save()
            except:
                pass
            auth.login(request, usr)
            messages.success(request, "You are logged in")
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query

                params = dict(x.split("=") for x in query.split("&"))

                if "next" in params:
                    nextPage = params["next"]
                    return redirect(nextPage)
            except:
                return redirect(home)

        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
    else:
        context = {}
    return render(request, "stylaza/login.html", {})


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.warning(request, "you are logged out")
    return redirect("/")


def about(request):
    return render(request, "stylaza/about.html")


def contact(request):
    return render(request, "stylaza/contact.html")


def shop(request, category_slug=None, brand_slug=None):
    categories = None
    products = None
    brands = None

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)

        products = Product.objects.filter(category=categories, is_available=True)
        for product in products:
            if product.Offer_Price():
                new = Product.Offer_Price(product)
                product.offer_price = new["new_price"]
                product.percentage = new["discount"]
                product.save()
            else:
                product.offer_price = 0
                product.save()

        paginator = Paginator(products, 6)
        page = request.GET.get("page")
        paged_products = paginator.get_page(page)
        product_count = products.count()
    elif brand_slug is not None:
        brands = get_object_or_404(Brand, slug=brand_slug)
        products = Product.objects.all().filter(brand=brands, is_available=True)
        for product in products:
            if product.Offer_Price():
                new = Product.Offer_Price(product)
                product.offer_price = new["new_price"]
                product.percentage = new["discount"]
                product.save()
            else:
                product.offer_price = 0
                product.save()
        paginator = Paginator(products, 6)
        page = request.GET.get("page")
        paged_products = paginator.get_page(page)  #
        product_count = products.count()
    else:

        products = Product.objects.all().filter(is_available=True).order_by("id")
        for product in products:
            if product.Offer_Price():
                new = Product.Offer_Price(product)
                product.offer_price = new["new_price"]
                product.percentage = new["discount"]

                product.save()
            else:
                product.offer_price = 0

                product.save()

        paginator = Paginator(products, 6)
        page = request.GET.get("page")
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        "products": paged_products,
        "product_count": product_count,
    }
    return render(request, "stylaza/shop-sidebar.html", context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug
        )
        images = []
        images.append(single_product.images)
        images.append(single_product.images1)
        images.append(single_product.images2)
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product
        ).exists()

    except Exception as e:
        raise e
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        "single_product": single_product,
        "in_cart": in_cart,
        "product_gallery": product_gallery,
        "images": images,
    }

    return render(request, "stylaza/product-single.html", context)


def home(request):
    products = Product.objects.all().filter(featured=True)
    for product in products:
        if product.Offer_Price():
            new = Product.Offer_Price(product)
            product.offer_price = new["new_price"]
            product.percentage = new["discount"]
            product.save()
        else:
            product.offer_price = 0
            product.save()
    categories = Category.objects.all()
    context = {
        "products": products,
        "categories": categories,
    }
    return render(request, "stylaza/index.html", context)


@login_required(login_url="login")
def checkout(request, total=0, quantity=0, cart_items=None):
    if request.user.is_authenticated:
        try:

            tax = 0
            grand_total = 0
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user, is_active=True)
                if "coupon_code" in request.session:

                    coupon = Coupon.objects.get(
                        coupon_code=request.session["coupon_code"]
                    )
                    reduction = coupon.discount

                else:
                    reduction = 0
                    coupon = "No Coupon"
            else:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            for cart_item in cart_items:
                if cart_item.product.offer_price == 0:
                    total += cart_item.product.price * cart_item.quantity
                else:
                    total += cart_item.product.offer_price * cart_item.quantity

                quantity += cart_item.quantity
            tax = (2 * total) / 100
            grand_total = total + tax - reduction
        except ObjectDoesNotExist:
            pass

        context = {
            "total": total,
            "quantity": quantity,
            "cart_items": cart_items,
            "tax": tax,
            "grand_total": grand_total,
            "coupon": coupon,
        }
        return render(request, "stylaza/checkout.html", context)
    else:
        return redirect("login")


@login_required(login_url="login")
def place_order(request, total=0, quantity=0, reduction=0):
    if request.user.is_authenticated:
        current_user = request.user

        cart_items = CartItem.objects.filter(user=current_user)
        cart_count = cart_items.count()
        if cart_count <= 0:
            return redirect("shop")
        grand_total = 0
        tax = 0
        if "coupon_code" in request.session:
            coupon = Coupon.objects.get(coupon_code=request.session["coupon_code"])
            reduction = coupon.discount

        else:
            coupon = "No Coupon"
            reduction = 0
        for cart_item in cart_items:
            if cart_item.product.Offer_Price():
                offer_price = Product.Offer_Price(cart_item.product)

                total = total + (offer_price["new_price"] * cart_item.quantity)

            else:
                total = total + (cart_item.product.price * cart_item.quantity)

            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = round(total + tax - reduction)

        if request.method == "POST":
            form = OrderForm(request.POST)
            if form.is_valid():
                data = Order()
                data.user = current_user
                data.first_name = form.cleaned_data["first_name"]
                data.last_name = form.cleaned_data["last_name"]
                data.phone = form.cleaned_data["phone"]
                data.email = form.cleaned_data["email"]
                data.address_line_1 = form.cleaned_data["address_line_1"]
                data.address_line_2 = form.cleaned_data["address_line_2"]
                data.country = form.cleaned_data["country"]
                data.state = form.cleaned_data["state"]
                data.city = form.cleaned_data["city"]
                data.order_note = form.cleaned_data["order_note"]
                data.order_total = grand_total
                data.tax = tax
                data.ip = request.META.get("REMOTE_ADDR")
                data.save()

                yr = int(datetime.date.today().strftime("%Y"))
                dt = int(datetime.date.today().strftime("%d"))
                mt = int(datetime.date.today().strftime("%m"))
                d = datetime.date(yr, mt, dt)
                current_date = d.strftime("%Y%m%d")
                order_number = current_date + str(data.id)

                request.session["ordernumber"] = order_number
                req = request.session["ordernumber"]

                data.order_number = order_number
                data.save()

                order = Order.objects.get(
                    user=current_user, is_ordered=False, order_number=order_number
                )
                context = {
                    "order": order,
                    "cart_items": cart_items,
                    "total": total,
                    "tax": tax,
                    "grand_total": grand_total,
                    "coupon": coupon,
                }
                messages.success(request, "Your order has been placed")
                return render(request, "stylaza/payments.html", context)
            else:
                messages.info(request, "Login to your account ")
                return redirect("checkout")
    else:
        return redirect("login")


@login_required(login_url="login")
def payments(request):
    if request.user.is_authenticated:
        body = json.loads(request.body)

        order = Order.objects.get(
            user=request.user, is_ordered=False, order_number=body["orderID"]
        )

        payment = Payment(
            user=request.user,
            payment_id=body["transID"],
            payment_method=body["payment_method"],
            amount_paid=order.order_total,
            status=body["status"],
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            if item.product.Offer_Price():
                offer_price = Product.Offer_Price(item.product)
                price = offer_price["new_price"]
                orderproduct.product_price = price
            else:
                orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        CartItem.objects.filter(user=request.user).delete()
        messages.success(request, "Payment is successful")
        data = {
            "order_number": order.order_number,
            "transID": payment.payment_id,
        }

        return JsonResponse(data)
    else:
        messages.info(request, "Login to your account")
        return redirect("login")


@login_required(login_url="login")
def payment_cod(request):
    if request.user.is_authenticated:
        current_user = request.user
        # generate order number
        order_number = request.session["ordernumber"]

        # move cart items to order product table
        cart_items = CartItem.objects.filter(user=current_user)
        order = Order.objects.get(
            user=request.user, is_ordered=False, order_number=order_number
        )

        # save payment informations
        payment = Payment(
            user=current_user,
            payment_method="Cash On Delivery",
            amount_paid=order.order_total,
            status="CASH ON DELIVERY",
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            if item.product.Offer_Price():
                offer_price = Product.Offer_Price(item.product)
                price = offer_price["new_price"]
                orderproduct.product_price = price
            else:
                orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        CartItem.objects.filter(user=request.user).delete()
        messages.success(request, "Order Success")

        # redirect_url = reverse("order_complete")
        return redirect("order_complete_cod")
    else:
        messages.info(request, "Login to your account for ordering products")
        return redirect("login")


@login_required(login_url="login")
def order_complete_cod(request):
    if request.user.is_authenticated:

        order_number = request.session["ordernumber"]

        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
            "order": order,
            "ordered_products": ordered_products,
            "order_number": order_number,
            "subtotal": subtotal,
        }
        if "coupon_code" in request.session:

            used_coupons = UsedCoupon()
            coupon = Coupon.objects.get(coupon_code=request.session["coupon_code"])

            used_coupons.coupon = coupon
            used_coupons.user = request.user
            used_coupons.save()

            del request.session["coupon_code"]

        return render(request, "stylaza/confirmation-cod.html", context)
    else:
        return redirect("login")


@login_required(login_url="login")
def order_complete(request):
    if request.user.is_authenticated:
        order_number = request.GET.get("order_number")
        transID = request.GET.get("payment_id")

        try:
            order = Order.objects.get(order_number=order_number, is_ordered=True)
            ordered_products = OrderProduct.objects.filter(order_id=order.id)

            subtotal = 0
            for i in ordered_products:
                subtotal += i.product_price * i.quantity
            payment = Payment.objects.get(payment_id=transID)
            context = {
                "order": order,
                "ordered_products": ordered_products,
                "order_number": order_number,
                "transID": payment.payment_id,
                "payment": payment,
                "subtotal": subtotal,
            }
            if "coupon_code" in request.session:

                used_coupons = UsedCoupon()
                coupon = Coupon.objects.get(coupon_code=request.session["coupon_code"])

                used_coupons.coupon = coupon
                used_coupons.user = request.user
                used_coupons.save()

                del request.session["coupon_code"]

            return render(request, "stylaza/confirmation.html", context)
        except (Payment.DoesNotExist, Order.DoesNotExist):
            return redirect("home")
    else:
        return redirect("login")


@login_required(login_url="login")
def dashboard(request):
    if request.user.is_authenticated:
        userprofile = get_object_or_404(UserProfile, user=request.user)
        orders = Order.objects.order_by("-created_at").filter(
            user_id=request.user.id, is_ordered=True
        )
        orders_count = orders.count()
        context = {
            "orders_count": orders_count,
            "userprofile": userprofile,
        }
        return render(request, "stylaza/dashboard.html", context)
    else:
        return redirect("login")


@login_required(login_url="login")
def my_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
            "-created_at"
        )
        cancelled_orders = Order.objects.filter(
            user=request.user, is_ordered=False
        ).order_by("-created_at")
        context = {
            "orders": orders,
            "cancelled_orders": cancelled_orders,
        }
        return render(request, "stylaza/order.html", context)
    else:
        return redirect("login")


@login_required(login_url="login")
def order_return(request, order_id):
    if request.user.is_authenticated:
        order = Order.objects.get(order_number=order_id)
        order_products = OrderProduct.objects.filter(order__order_number=order_id)
        order.return_status = True
        order.status = "Waiting for return"
        order.save()
        messages.warning(request, "You have requested for a return ")
        for order_product in order_products:
            order_product.product.stock += order_product.quantity
            order_product.return_status = True
            order_product.product.save()
        return redirect(my_orders)
    else:
        messages.info(request, "Login to your account for returning your order")
        return redirect("login")


@login_required(login_url="login")
def cancel_return(request, order_id):
    if request.user.is_authenticated:
        order = Order.objects.get(order_number=order_id)
        order_products = OrderProduct.objects.filter(order__order_number=order_id)
        order.return_status = False
        order.status = "Delivered"
        order.save()
        messages.warning(request, "Your return have been cancelled ")
        for order_product in order_products:
            order_product.product.stock += order_product.quantity
            order_product.return_status = False
            order_product.product.save()
        return redirect(my_orders)
    else:
        messages.info(request, "Login to your account for cancelling the returns")
        return redirect("login")


@login_required(login_url="login")
def order_detail(request, order_id):
    if request.user.is_authenticated:
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
        return render(request, "stylaza/order_detail.html", context)
    else:
        return redirect("login")


@login_required(login_url="login")
def order_cancel(request, order_id):
    if request.user.is_authenticated:
        order = Order.objects.get(order_number=order_id, is_ordered=True)
        order_products = OrderProduct.objects.filter(order__order_number=order_id)
        order.status = "Cancelled"
        order.payment.status = "REFUNDED"
        order.is_ordered = False
        order.save()
        order.payment.save()
        messages.warning(request, "Order has been cancelled")
        for order_product in order_products:
            order_product.ordered = False
            order_product.product.stock += order_product.quantity
            order_product.product.save()
        return redirect(my_orders)
    else:
        messages.info(request, "Login to your account for order cancellation")
        return redirect("login")


def search(request):
    keyword = request.GET["key"]
    if keyword:
        products = Product.objects.order_by("id").filter(
            Q(product_name__icontains=keyword)
        )
        product_count = products.count()
        context = {
            "products": products,
            "product_count": product_count,
        }
        return render(request, "stylaza/shop-sidebar.html", context)
    else:
        return redirect("shop")


@login_required(login_url="login")
def edit_profile(request):
    if request.user.is_authenticated:
        userprofile = get_object_or_404(UserProfile, user=request.user)
        if request.method == "POST":
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(
                request.POST, request.FILES, instance=userprofile
            )
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Your profile has been updated")
                return redirect("profile-details")
        else:
            user_form = UserForm(instance=request.user)
            profile_form = UserProfileForm(instance=userprofile)
        context = {
            "user_form": user_form,
            "profile_form": profile_form,
            "userprofile": userprofile,
        }
        return render(request, "stylaza/edit_profile.html", context)
    else:
        return redirect("login")


@login_required(login_url="login")
def profile_details(request):
    if request.user.is_authenticated:
        userprofile = get_object_or_404(UserProfile, user=request.user)
        context = {
            "userprofile": userprofile,
        }
        return render(request, "stylaza/profile-details.html", context)
    else:
        return redirect("login")


@login_required(login_url="login")
def change_password(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            current_password = request.POST["current_password"]
            new_password = request.POST["new_password"]
            confirm_password = request.POST["confirm_password"]

            user = Account.objects.get(username__exact=request.user.username)

            if new_password == confirm_password:
                success = user.check_password(current_password)
                if success:
                    user.set_password(new_password)
                    user.save()
                    auth.logout(request)
                    messages.success(request, "Password updated successfully")
                    return redirect("login")
                else:
                    messages.error(request, "Please enter valid current password")
                    return redirect("change-password")
            else:
                messages.error(request, "Password does not match")
                return redirect("change-password")

        return render(request, "stylaza/forget-password.html")
    else:
        return redirect("login")


# Wishlist
@login_required(login_url="login")
def add_wishlist(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    print("first")
    print(product)
    w_list = Wishlist.objects.filter(product=product, user=current_user)
    print("second")
    print(w_list)
    if w_list:
        wish_list = Wishlist.objects.filter(user=request.user).order_by("-id")
        messages.info(request, "Product is already in the wishlist")
        return redirect(my_wishlist)
    else:
        wish_item = Wishlist.objects.create(product=product, user=current_user)
        wish_item.save()
        messages.success(request, "Product is added to wishlist")
        wish_list = Wishlist.objects.filter(user=request.user).order_by("-id")
        return render(request, "stylaza/wishlist.html", {"wish_list": wish_list})


# My Wishlist
def my_wishlist(request):
    if request.user.is_authenticated:
        wish_list = Wishlist.objects.filter(user=request.user).order_by("-id")
        return render(request, "stylaza/wishlist.html", {"wish_list": wish_list})
    else:
        return render(request, "stylaza/wishlist.html")


@login_required(login_url="login")
def remove_wish_list(request, product_id, wishlist_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        wish_item = Wishlist.objects.get(
            product=product, user=request.user, id=wishlist_id
        )
        wish_item.delete()
        messages.error(request, "Product is removed from wishlist")
        return redirect("wishlist")
    else:
        return redirect("shop")

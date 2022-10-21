from django import forms
from account.models import Account
from web.models import Order, ProductOffer, CategoryOffer, BrandOffer
from django.forms import ModelForm


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm Password", "class": "form-control"}
        )
    )

    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone_number", "email", "password"]

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("password does not match!")

    def __init__(self, *arg, **kwargs):
        super(RegistrationForm, self).__init__(*arg, **kwargs)
        self.fields["first_name"].widget.attrs["placeholder"] = "Enter First Name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter Last Name"
        self.fields["email"].widget.attrs["placeholder"] = "Enter Email"
        self.fields["phone_number"].widget.attrs[
            "placeholder"
        ] = "Enter your Phone Number"

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "address_line_1",
            "address_line_2",
            "country",
            "state",
            "city",
            "order_note",
        ]


class StatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status"]


class BrandOfferForm(ModelForm):
    class Meta:
        model = BrandOffer
        fields = ["brand_name", "discount"]


class CategoryOfferForm(ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ["category_name", "discount"]


class ProductOfferForm(ModelForm):
    class Meta:
        model = ProductOffer
        fields = ["product_name", "discount"]

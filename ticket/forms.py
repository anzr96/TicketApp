from django import forms
from django.utils.translation import gettext as _


class SalonForms(forms.Form):
    name = forms.CharField(max_length=50)
    english_name = forms.CharField(max_length=50)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(max_length=300, required=False)
    postal_code = forms.CharField(max_length=10, required=False)
    next = forms.CharField(max_length=20)


class UserForms(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone_number = forms.CharField(max_length=15)
    email = forms.EmailField(required=False)
    birthday = forms.DateField(required=False)
    role = forms.CharField(max_length=10)
    salon = forms.CharField(max_length=50)


class ServiceForm(forms.Form):
    code = forms.CharField(max_length=50)
    name = forms.CharField(max_length=50)
    price = forms.IntegerField(required=False)
    description = forms.CharField(max_length=255, required=False)


class UserDataForm(forms.Form):
    phone_number = forms.CharField(max_length=15, required=False)
    qr = forms.CharField(max_length=100, required=False)


class SubFactorForm(forms.Form):
    username = forms.CharField(max_length=50)
    service = forms.CharField(max_length=50)
    stylist = forms.CharField(max_length=50, required=False)
    number = forms.IntegerField()
    price = forms.IntegerField()
    discount = forms.IntegerField()
    side_fees = forms.IntegerField()
    discount_percent = forms.IntegerField()
    discount_amount = forms.IntegerField()


class UpdateSubFactorForm(forms.Form):
    id = forms.IntegerField()
    side_fees = forms.IntegerField()
    discount_percent = forms.IntegerField()
    discount_amount = forms.IntegerField()
    next = forms.CharField(max_length=255)


class UpdateFactorForm(forms.Form):
    code = forms.CharField(max_length=100)
    payment_method = forms.CharField(max_length=20)
    paid_amount = forms.IntegerField()
    next = forms.CharField(max_length=255)


class ProfileForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50)

    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(max_length=12)
    birthday = forms.DateField(required=False)

    address = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=50, required=False)
    state = forms.CharField(max_length=50, required=False)
    postal_code = forms.CharField(max_length=10, required=False)

    card_number = forms.CharField(max_length=16, required=False)
    account_number = forms.CharField(max_length=20, required=False)
    shaba_number = forms.CharField(max_length=50, required=False)


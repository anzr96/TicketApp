from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import datetime
from django.utils import timezone


# Create your models here.
class Salon(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    english_name = models.CharField(max_length=50, null=False, blank=True, unique=True)
    logo = models.ImageField(null=True, blank=True, default='/static/ticket/images/logo/logo_tag.png')


class User(AbstractUser):
    profile_photo = models.ImageField(null=True, blank=True, default='/static/ticket/images/profile/girl.png')
    phone_number = models.CharField(max_length=20, null=False, blank=False, unique=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)

    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'phone_number', 'first_name', 'last_name', 'password']


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin')


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='customer_manager')


class Accountant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='accountant_manager')


class Service(models.Model):
    code = models.CharField(max_length=50, null=False, blank=False)
    name = models.CharField(max_length=50, null=False, blank=False)
    created_date = models.DateTimeField(editable=False)
    modified_date = models.DateTimeField()
    description = models.CharField(max_length=300, null=True, blank=True)
    offeredـprice = models.IntegerField(null=True, blank=True)

    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)

    def save(self, **kwargs):
        if not self.id:
            self.created_date = timezone.now()
        self.modified_date = timezone.now()
        super(Service, self).save()


class Factor(models.Model):
    NOT_PAID = 'پرداخت نشده'
    UNCOMPLETE = 'نیمه تمام'
    COMPLETE = 'پرداخت شده'
    STATUS = (
        (NOT_PAID, 'NP'),
        (UNCOMPLETE, 'UC'),
        (COMPLETE, 'C'),
    )
    CASH = 'نقدی'
    POS = 'دستگاه کارت خوان'
    ONLINE = 'درگاه آنلاین'
    CARD_TO_CARD = 'کارت به کارت'
    PAYMENT_METHOD = (
        (CASH, 'CASH'),
        (POS, 'POS'),
        (CARD_TO_CARD, 'CTC'),
        (ONLINE, 'ON'),
    )

    code = models.CharField(max_length=50, null=False, blank=False)
    created_date = models.DateTimeField(editable=False)
    modified_date = models.DateTimeField()
    total_amount = models.IntegerField(default=0)
    discount_percent = models.IntegerField(default=0)
    discount_amount = models.IntegerField(default=0)
    final_amount = models.IntegerField(default=0)
    paid_amount = models.IntegerField(default=0)
    status = models.CharField(max_length=2, choices=STATUS, default=NOT_PAID)
    payment_method = models.CharField(max_length=4, choices=PAYMENT_METHOD, default=POS)
    description = models.CharField(max_length=300, null=True, blank=True)

    customer_factors = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, related_name='factors')
    accountants = models.ForeignKey(Accountant, on_delete=models.DO_NOTHING, related_name='factors', null=True,
                                    blank=True)

    def save(self, **kwargs):
        if not self.id:
            self.created_date = timezone.now()
        self.modified_date = timezone.now()
        super(Factor, self).save()


class SubFactor(models.Model):
    index = models.IntegerField()
    created_date = models.DateTimeField(editable=False)
    modified_date = models.DateTimeField()
    final_amount = models.IntegerField()
    discount_percent = models.IntegerField()
    discount_amount = models.IntegerField()
    side_fees = models.IntegerField()
    total = models.IntegerField()

    factors = models.ForeignKey(Factor, on_delete=models.DO_NOTHING, related_name='sub_factors')

    def save(self, **kwargs):
        if not self.id:
            self.created_date = timezone.now()
        self.modified_date = timezone.now()
        super(SubFactor, self).save()


class SubService(models.Model):
    number = models.IntegerField()
    price = models.IntegerField()
    discount = models.IntegerField()
    description = models.CharField(max_length=255, null=True, blank=True)

    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING, related_name='sub_services')
    subFactor = models.ForeignKey(SubFactor, on_delete=models.DO_NOTHING, related_name='sub_services')


class Stylist(models.Model):
    role = models.CharField(max_length=20, null=False, blank=False)

    sub_factors = models.ManyToManyField(SubFactor)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='stylist_manager')
    services = models.ManyToManyField(Service, through='StylistService')


class StylistService(models.Model):
    stylist = models.ForeignKey(Stylist, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    percent = models.IntegerField()


class QRCode(models.Model):
    code = models.CharField(max_length=256, null=False, blank=False)
    created_date = models.DateTimeField(editable=False)
    modified_date = models.DateTimeField()

    admin = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)

    def save(self, **kwargs):
        if not self.id:
            self.created_date = timezone.now()
        self.modified_date = timezone.now()
        super(QRCode, self).save()


class Contact(models.Model):
    phone_number = models.CharField(max_length=12, null=True, blank=True)
    address1 = models.CharField(max_length=255, null=True, blank=True)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    bio = models.CharField(max_length=255, null=True, blank=True)

    salons = models.ForeignKey(Salon, on_delete=models.CASCADE, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)


class BankInfo(models.Model):
    card_number = models.CharField(max_length=16, null=True, blank=True)
    account_number = models.CharField(max_length=20, null=True, blank=True)
    shaba_number = models.CharField(max_length=50, null=True, blank=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Tag(models.Model):
    name = models.CharField(max_length=50)

    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)


class Portfolio(models.Model):
    image = models.ImageField(upload_to='portfolio/')
    name = models.CharField(max_length=50, null=True, blank=True)

    tag = models.ForeignKey(Tag, on_delete=models.DO_NOTHING)
    sub_service = models.ForeignKey(SubService, on_delete=models.DO_NOTHING)


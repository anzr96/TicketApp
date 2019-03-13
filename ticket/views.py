from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.views import LoginView
from ticket.forms import *
from ticket.models import *
from django.shortcuts import redirect
import string, random, decimal
from django.contrib.auth.models import Group
import qrcode
from datetime import date, datetime, timedelta
import hashlib
import json
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core import serializers
import time
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

FORM_INVALID = 'اطلاعات وارد شده صحیح نمی باشند'


# Create your views here.
def password_generator(size=8, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for i in range(size))


def random_number(size=4, chars=string.digits):
    return ''.join(random.choice(chars) for i in range(size))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class HomeView(TemplateView):
    template_name = "ticket/index.html"

    def get(self, request, *args, **kwargs):
        messages.add_message(request, messages.INFO,
                             str(request.user.first_name) + ' ' + str(request.user.last_name) + ' عزیز خوش آمدید')
        try:
            (request.user.customer is None)
            return redirect('/view-profile/')
        except:
            pass
        salon = Salon.objects.get(user=request.user)
        useful_link = request.GET.get('useful_link')

        if useful_link is not None:
            if useful_link == 'today':
                factors = Factor.objects.filter(customer_factors__user__salon=salon,
                                                created_date__date=date.today()).order_by('created_date').all()
            elif useful_link == 'yesterday':
                factors = Factor.objects.filter(customer_factors__user__salon=salon,
                                                created_date__date=(date.today() - timedelta(days=1))).order_by(
                    'created_date').all()
            elif useful_link == 'this_week':
                factors = Factor.objects.filter(customer_factors__user__salon=salon, created_date__gt=(date.today()
                                                                                                       - timedelta(
                            days=7)), created_date__lt=date.today() + timedelta(days=1)).order_by('created_date').all()
            elif useful_link == 'uc':
                factors = Factor.objects.filter(customer_factors__user__salon=salon) \
                    .exclude(status='C').order_by('created_date').all()
            else:
                factors = Factor.objects.filter(customer_factors__user__salon=salon).order_by('created_date').all()[
                          :100]
        else:
            factors = Factor.objects.filter(customer_factors__user__salon=salon,
                                            created_date__date=date.today()).order_by('created_date').all()

        return render(request, self.template_name, {'factors': factors})

    def post(self, request, *args, **kwargs):
        salon = Salon.objects.get(user=request.user)

        factors = Factor.objects.filter(customer_factors__user__salon=salon).all()[:100]
        serialized_factors = serializers.serialize('json', factors)

        return JsonResponse(serialized_factors, safe=False)


class AddUserView(TemplateView):
    form_class = UserForms
    template_name = 'ticket/addUser.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        roles = []

        if user.is_superuser:
            salons = Salon.objects.all()
        else:
            salons = Salon.objects.filter(users__username=request.user.username)

        if user.has_perm('ticket.add_manager'):
            role = {'name': 'مدیر', 'value': 'manager', 'id': '1'}
            roles.append(role)

            role = {'name': 'آرایشگر', 'value': 'stylist', 'id': '2'}
            roles.append(role)

            role = {'name': 'مشتری', 'value': 'customer', 'id': '3'}
            roles.append(role)

            role = {'name': 'حسابدار', 'value': 'accountant', 'id': '4'}
            roles.append(role)

        else:
            role = {'name': 'آرایشگر', 'value': 'stylist', 'id': '1'}
            roles.append(role)

            role = {'name': 'مشتری', 'value': 'customer', 'id': '2'}
            roles.append(role)

            role = {'name': 'حسابدار', 'value': 'accountant', 'id': '3'}
            roles.append(role)

        return render(request, self.template_name, {'roles': roles, 'salons': salons})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            birthday = form.cleaned_data['birthday']
            role = form.cleaned_data['role']
            password = phone_number
            salon_code = form.cleaned_data['salon']
            salon = Salon.objects.filter(code=salon_code).first()
            if salon is None:
                messages.add_message(request, messages.ERROR, 'سالن انتخاب نشده است')
                return redirect(request.path)

            username = phone_number + salon.code
            if role == "manager" and not request.user.has_perm('ticket.add_manager'):
                messages.add_message(request, messages.WARNING, 'شما این نقش را نمی توانید انتخاب کنید')
                raise form.ValidationError("شما این نقش را نمی توانید انتخاب کنید")

            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            phone_number=phone_number, email=email, birthday=birthday,
                                            password=password, salon=salon)
            user.profile_photo = '/uploads/default/girl.svg'
            group = Group.objects.get(name=role)
            user.groups.add(group)
            user.save()

            if role == "manager":
                user_admin = User.objects.get(username=request.user.username)
                manager = Manager.objects.create(user=user, admin=user_admin)
                manager.save()
                messages.add_message(request, messages.SUCCESS, 'مدیر جدید با موفقیت ثبت شد')
            elif role == "customer":
                user_admin = User.objects.get(username=request.user.username)
                customer = Customer.objects.create(user=user, manager=user_admin)
                customer.save()

                pre_qr = str(salon) + "." + str(phone_number) + "." + str(request.user.first_name) + str(
                    request.user.last_name) + "." + str(password_generator)
                hash_qr = hashlib.sha224(pre_qr.encode()).hexdigest()
                qr = QRCode.objects.create(code=hash_qr, customer=customer, admin=user_admin)
                qr.save()
                messages.add_message(request, messages.SUCCESS, 'مشتری جدید با موفقیت ثبت شد')
            elif role == "accountant":
                user_admin = User.objects.get(username=request.user.username)
                accountant = Accountant.objects.create(user=user, manager=user_admin)
                accountant.save()
                messages.add_message(request, messages.SUCCESS, 'حسابدار جدید با موفقیت ثبت شد')
            elif role == "stylist":
                user_admin = User.objects.get(username=request.user.username)
                stylist = Stylist.objects.create(user=user, manager=user_admin)
                stylist.save()
                messages.add_message(request, messages.SUCCESS, 'آرایشگر جدید با موفقیت ثبت شد')
            else:
                user.remove()
                messages.add_message(request, messages.ERROR, 'نقش انتخاب شده صحیح نیست')
                raise form.ValidationError('نقش انتخاب شده صحیح نیست')

            return redirect(request.path)
        messages.add_message(request, messages.WARNING, FORM_INVALID)
        return redirect(request.path)


class AddSalonView(TemplateView):
    form_class = SalonForms
    template_name = 'ticket/addSalon.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            address = form.cleaned_data['address']
            postal_code = form.cleaned_data['postal_code']
            english_name = form.cleaned_data['english_name']
            name = form.cleaned_data['name']
            english_name.join(('_', str(phone_number)))

            check = False
            number = 0
            while not check:
                number = random_number()
                check = Salon.objects.filter(code=str(number)).exists()

            salon = Salon.objects.create(code=str(number), name=name, english_name=english_name)
            salon.save()

            contact = Contact.objects.create(phone_number=phone_number, address1=address, postal_code=postal_code,
                                             salons=salon)
            contact.save()

            messages.add_message(request, messages.SUCCESS, 'سالن ' + name + ' با موفقیت ثبت شد')
            return redirect(form.cleaned_data['next'])
        messages.add_message(request, messages.WARNING, FORM_INVALID)
        return redirect(request.path)


class AddServiceView(TemplateView):
    template_name = "ticket/addService.html"
    form_class = ServiceForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            name = form.cleaned_data['name']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']

            salon = Salon.objects.filter(user=request.user).first()
            service = Service.objects.create(code=code, name=name, offeredـprice=price, description=description,
                                             salon=salon)
            try:
                service.save()
                messages.add_message(request, messages.SUCCESS, 'سرویس جدید با موفقیت ثبت شد')
            except:
                logger.exception('سرویس اضافه نشد')
                messages.add_message(request, messages.ERROR, 'خطا رخ داد')
                messages.add_message(request, messages.ERROR, 'سرویس جدید اضافه نشد. لطفا دوباره تلاش کنید')

            return redirect(request.path)
        messages.add_message(request, messages.WARNING, FORM_INVALID)
        return redirect(request.path)


class AddSubFactor(TemplateView):
    form_class = SubFactorForm
    template_name = "ticket/addSubFactor.html"

    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            stylist_exist = (user.stylist is not None)
        except:
            stylist_exist = False

        salon = Salon.objects.filter(user=request.user).first()

        if user.groups.filter(name='stylist').exists() and stylist_exist:
            services = Service.objects.filter(salon=salon, stylistservice__stylist__user=user)
        else:
            services = Service.objects.filter(salon=salon)
        if not user.groups.filter(name="stylist").exists():
            users = User.objects.filter(groups__name="stylist", salon=salon)
            return render(request, self.template_name, {'services': services, 'stylists': users})
        else:
            return render(request, self.template_name, {'services': services})

    def post(self, request, *args, **kwargs):
        stylist = User.objects.filter(username=request.user.username).first()
        json_parsed = json.loads(request.body)

        customer = User.objects.filter(username=json_parsed['username']).first()
        next_url = json_parsed['next']

        discount_amount = json_parsed['discount_amount']
        if not is_num(discount_amount):
            discount_amount = 0

        discount_percent = json_parsed['discount_percent']
        if not is_num(discount_percent):
            discount_percent = 0

        side_fees = json_parsed['side_fees']
        if not is_num(side_fees):
            side_fees = 0

        factor = Factor.objects.filter(customer_factors=customer.customer, status__in=['NP', 'UC'],
                                       created_date__date=date.today()).first()
        if factor is None:
            code = stylist.username + "-" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            factor = Factor.objects.create(code=code, customer_factors=customer.customer)
            factor.save()

        index = factor.sub_factors.count()
        sub_factor = SubFactor.objects.create(index=index, final_amount=0, discount_percent=discount_percent,
                                              discount_amount=discount_amount, side_fees=side_fees, total=0,
                                              factors=factor)
        i = 0
        total = 0
        for s in json_parsed['service']:
            service = Service.objects.filter(code=s, stylistservice__stylist__user=stylist).first()

            if service is None:
                messages.add_message(request, messages.WARNING, 'سرویس ' + s + ' در سیستم موجود نیست')
                continue

            number = json_parsed['number'][i]
            if not is_num(number):
                logger.info('number is not num : ' + number)
                messages.add_message(request, messages.ERROR, 'تعداد به درستی وارد نشده')
                return HttpResponse('#')

            price = json_parsed['price'][i]
            if not is_num(price):
                logger.info('price is not num : ' + price)
                messages.add_message(request, messages.ERROR, 'قیمت به درستی وارد نشده')
                return HttpResponse('#')

            discount = json_parsed['discount'][i]
            if not is_num(discount):
                discount = 0

            total += int(number) * int(price) * (100 - int(discount)) / 100
            sub_service = SubService.objects.create(number=number, price=price, discount=discount, service=service,
                                                    subFactor=sub_factor)

            description = json_parsed['description'][i]
            if description is not None:
                sub_service.description = description

            sub_service.save()
            i += 1

        sub_factor.total = total
        sub_factor.final_amount = total * (100 - int(discount_percent)) / 100 - int(discount_amount) + int(side_fees)
        sub_factor.save()

        factor.total_amount += total
        factor.final_amount += sub_factor.final_amount
        factor.save()

        messages.add_message(request, messages.SUCCESS, 'فاکتور جدید با موفقیت ثبت شد')
        return HttpResponse(next_url)


class GetServiceData(View):

    def post(self, request, *args, **kwargs):
        service_code = request.POST["service"]
        service = Service.objects.filter(code=service_code).first()
        if service is None:
            response = JsonResponse({})
            return response

        response = JsonResponse({'price': service.offeredـprice})
        return response


class GetUserData(View):

    def post(self, request, *args, **kwargs):
        form = UserDataForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            qr = form.cleaned_data['qr']
            if phone is not None:
                user = User.objects.filter(phone_number=phone).first()
            elif qr is not None:
                user = User.objects.filter(customer__qrcode=qr).first()
            else:
                return HttpResponse("Not Found", status=404)

            if not user.groups.filter(name="customer").exists():
                return HttpResponse("Not Found", status=404)

            response = JsonResponse(
                {'first_name': user.first_name, 'last_name': user.last_name, 'username': user.username})
            return response
        messages.add_message(request, messages.WARNING, FORM_INVALID)
        return redirect(request.path)


class UpdateFactorView(TemplateView):
    template_name = "ticket/updateFactors.html"
    form_class = UpdateFactorForm

    def get(self, request, *args, **kwargs):
        salon = Salon.objects.filter(user=request.user).first()
        code = request.GET.get('code')
        if code is None:
            messages.add_message(request, messages.WARNING, 'لطفا دوباره تلاش کنید')
            return redirect(request.path)

        factor = Factor.objects.filter(code=code, customer_factors__user__salon=salon).first()
        if factor is None:
            messages.add_message(request, messages.ERROR, 'فاکتور مورد نظر یافت نشد')
            return redirect(request.path)

        customer = factor.customer_factors.user
        accountant = User.objects.filter(username=request.user.username).first()

        subfactors = SubFactor.objects.filter(factors=factor)

        ps = Factor.PAYMENT_METHOD
        payments = []
        for p in ps:
            payments.append({'code': p[1], 'name': p[0]})

        return render(request, self.template_name, {'factor_code': factor.code,
                                                    'customer': customer.first_name + " " + customer.last_name,
                                                    'accountant': accountant.first_name + " " + accountant.last_name,
                                                    'created_date': factor.created_date,
                                                    'modified_date': factor.modified_date,
                                                    'factor_status': factor.status,
                                                    'total_amount': factor.total_amount,
                                                    'final_amount': factor.final_amount,
                                                    'remaining_amount': factor.final_amount - factor.paid_amount,
                                                    'subfactors': subfactors,
                                                    'payments': payments})

    def post(self, request, *args, **kwargs):
        salon = Salon.objects.filter(user=request.user).first()
        form = self.form_class(request.POST)
        if form.is_valid():
            factor = Factor.objects.get(code=form.cleaned_data['code'], customer_factors__user__salon=salon)
            factor.payment_method = form.cleaned_data['payment_method']
            paid_amount = form.cleaned_data['paid_amount']

            paid_amount += factor.paid_amount
            if paid_amount < factor.final_amount:
                factor.paid_amount = paid_amount
                factor.status = 'UC'
                factor.modified_date = timezone.now()

            elif paid_amount > factor.final_amount:
                messages.add_message(request, messages.ERROR, 'مقدار پرداخت شده از مقدار فاکتور بیشتر است')
                return HttpResponse('fail')
            else:
                factor.paid_amount = paid_amount
                factor.status = 'C'
                factor.modified_date = timezone.now()

            factor.save()
            messages.add_message(request, messages.SUCCESS, 'فاکتور با موفقیت بروزرسانی شد')
            return redirect(form.cleaned_data['next'])
        messages.add_message(request, messages.WARNING, FORM_INVALID)
        return redirect(request.path)


class UpdateSubFactorView(View):
    form_class = UpdateSubFactorForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            subfactor = SubFactor.objects.get(pk=form.cleaned_data['id'])
            subfactor.side_fees = form.cleaned_data['side_fees']
            subfactor.discount_percent = form.cleaned_data['discount_percent']
            subfactor.discount_amount = form.cleaned_data['discount_amount']
            subfactor.final_amount = subfactor.total * (
                    100 - subfactor.discount_percent) / 100 - subfactor.discount_amount + subfactor.side_fees
            subfactor.save()

            factor = subfactor.factors
            factor.final_amount = calculate_final_amount(factor)
            factor.save()

            return redirect(form.cleaned_data['next'])
        messages.add_message(request, messages.WARNING, FORM_INVALID)
        return redirect(request.path)


class ViewFactorView(TemplateView):
    template_name = 'ticket/viewFactor.html'

    def get(self, request, *args, **kwargs):
        phone_number = request.GET.get('phone_number')
        qr_code = request.GET.get('qr')
        salon = Salon.objects.get(user=request.user)

        if request.user.groups.filter(name="stylist").exist() and not request.user.is_superuser:
            if phone_number is not None:
                user = User.objects.filter(phone_number=phone_number).first()
                if not user.groups.filter(name="customer").exists():
                    return redirect('/')
                factors = Factor.objects.filter(customer_factors__user__salon=salon, customer_factors=user.customer,
                                                sub_factors__stylist__user=request.user).exclude(status='C')
            elif qr_code is not None:
                customer = Customer.objects.filter(qrcode=qr_code).first()
                factors = Factor.objects.filter(customer_factors__user__salon=salon, customer_factors=customer
                                                , sub_factors__stylist__user=request.user).exclude(status='C')
            else:
                factors = Factor.objects.filter(customer_factors__user__salon=salon
                                                , sub_factors__stylist__user=request.user).exclude(status="C")
        else:
            if phone_number is not None:
                user = User.objects.filter(phone_number=phone_number).first()
                if not user.groups.filter(name="customer").exists():
                    return redirect('/')
                factors = Factor.objects.filter(customer_factors__user__salon=salon,
                                                customer_factors=user.customer).exclude(status='C')
            elif qr_code is not None:
                customer = Customer.objects.filter(qrcode=qr_code).first()
                factors = Factor.objects.filter(customer_factors__user__salon=salon, customer_factors=customer).exclude(
                    status='C')
            else:
                factors = Factor.objects.filter(customer_factors__user__salon=salon).exclude(status="C")

        return render(request, self.template_name, {'title': 'مشاهده فاکتور',
                                                    'factors': factors})


class ViewProfileView(TemplateView):
    template_name = 'ticket/profile.html'

    def get(self, request, *args, **kwargs):
        username = request.GET.get('username')

        if username is None:
            user = request.user
            title = 'پروفایل من'
        else:
            user = User.objects.get(username=username)
            if user is None:
                messages.add_message(request, messages.WARNING, 'کاربر مورد نظر یافت نشد')
                return redirect('/')
            title = 'پروفایل ' + user.first_name + " " + user.last_name

        try:
            (request.user.customer is not None)
            qr_code = request.user.customer.qrcode.code
        except:
            qr_code = None

        return render(request, self.template_name, {'title': title,
                                                    'qr_code': qr_code, 'user': user})


class UpdateProfileView(TemplateView):
    form_class = ProfileForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']

            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            postal_code = form.cleaned_data['postal_code']

            card_number = form.cleaned_data['card_number']
            account_number = form.cleaned_data['account_number']
            shaba_number = form.cleaned_data['shaba_number']

            user = User.objects.get(username=username)
            if user.check_password(password) and request.user.username == username:
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.phone_number = phone_number
                user.save()

                if address is not None or city is not None or state is not None or postal_code is not None:
                    contact = Contact.objects.create(address1=address, city=city, state=state, postal_code=postal_code,
                                                     user=user)

                if card_number is not None or account_number is not None or shaba_number is not None:
                    bank_info = BankInfo.objects.create(card_number=card_number, account_number=account_number,
                                                        shaba_number=shaba_number, user=user)
            else:
                messages.add_message(request, messages.ERROR, 'شما دسنرسی ندارید')
                logger.warning('کاربر ' + request.user.username + ' با IP ' + get_client_ip(request) + 'درخواست تغییر '
                                                                                                       'پروفایل ' +
                               username + ' را داشت')
                return redirect('/')
            messages.add_message(request, messages.SUCCESS, 'اطلاعات شما با موفقیت تغییر پیدا کرد')
            return redirect('/view-profile/')
        messages.add_message(request, messages.WARNING, FORM_INVALID)
        return redirect(request.path)


class AddServiceStylist(TemplateView):
    template_name = 'ticket/addServiceStylist.html'

    def get(self, request, *args, **kwargs):
        salon = request.user.salon
        stylists = User.objects.filter(groups__name='stylist', salon=salon)
        services = Service.objects.filter(salon=salon)
        return render(request, self.template_name, {'stylists': stylists, 'services': services})

    def post(self, request, *args, **kwargs):
        json_parsed = json.loads(request.body)

        i = 0
        for s in json_parsed['stylist']:
            stylist = Stylist.objects.get(user__username=s)
            service = Service.objects.get(code=json_parsed['service'][i])
            percent = json_parsed['percent'][i]
            StylistService.objects.create(stylist=stylist, service=service, percent=percent)
            i += 1

        messages.add_message(request, messages.SUCCESS, 'سرویس ها با موفقیت به آرایشگران اختصاص داده شدند')
        return HttpResponse(json_parsed['next'])


class ViewCustomerView(TemplateView):
    template_name = 'ticket/viewCustomer.html'

    def get(self, request, *args, **kwargs):
        salon = Salon.objects.get(user=request.user)

        users = User.objects.filter(salon=salon, groups__name='customer', customer__isnull=False).distinct()

        users2 = []
        for user in users:
            username = user.username
            first_name = user.first_name
            last_name = user.last_name
            phone_number = user.phone_number

            factor_last = Factor.objects.filter(customer_factors=user.customer).order_by('-created_date').first()
            if factor_last is not None:
                last_time = factor_last.created_date
            else:
                last_time = '-'

            factor_status = Factor.objects.filter(customer_factors=user.customer, status__in=['NP', 'UC']) \
                .order_by('-created_date').first()
            if factor_status is not None:
                status = factor_status.status
            else:
                status = '-'

            users2.append({'username': username, 'first_name': first_name, 'last_name': last_name,
                           'phone_number': phone_number, 'last_time': last_time, 'status': status})

        return render(request, self.template_name, {'users': users2})


class ViewEmployView(TemplateView):
    template_name = 'ticket/viewEmploy.html'

    def get(self, request, *args, **kwargs):
        salon = Salon.objects.get(user=request.user)

        users = User.objects.filter(salon=salon, groups__name__in=['stylist', 'accountant']).distinct()

        users2 = []
        for user in users:
            username = user.username
            first_name = user.first_name
            last_name = user.last_name
            phone_number = user.phone_number
            role = user.groups.first().name

            services = Service.objects.filter(stylistservice__stylist__user=user)[:3]
            service = ', '.join(str(service.name) for service in services if service is not None)

            subfactors = SubFactor.objects.filter(stylist__user=user, created_date__date=date.today())

            total = 0
            for subfactor in subfactors:
                total += subfactor.final_amount

            users2.append({'username': username, 'first_name': first_name, 'last_name': last_name,
                           'phone_number': phone_number, 'service': service, 'income': total, 'role': role})

        return render(request, self.template_name, {'users': users2})


def create_qr_img(hash_str):
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=4,
                       )

    qr.add_data(hash_str)
    qr.make(fit=True)
    return qr.make_image()


def is_num(data):
    try:
        int(data)
        return True
    except ValueError:
        return False


def calculate_final_amount(factor):
    final_amount = 0
    for subfactor in factor.sub_factors.all():
        final_amount += subfactor.final_amount
    return final_amount

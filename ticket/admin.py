from django.contrib import admin
from django.contrib.auth.models import Permission
from ticket.models import *

# Register your models here.
admin.site.register(Permission)
admin.site.register(User)
admin.site.register(Salon)
admin.site.register(Manager)
admin.site.register(Accountant)
admin.site.register(Stylist)
admin.site.register(Customer)
admin.site.register(QRCode)
admin.site.register(Factor)
admin.site.register(SubFactor)
admin.site.register(SubService)
admin.site.register(Service)
admin.site.register(Contact)

from django.urls import path, include
from ticket.views import *
from django.contrib.auth.decorators import login_required, permission_required

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', include('pwa.urls')),
    path("add-user/", permission_required('ticket.add_user', raise_exception=True)(AddUserView.as_view())),
    path("add-salon/", permission_required('ticket.add_salon', raise_exception=True)(AddSalonView.as_view())),
    path("add-service/", permission_required('ticket.add_service', raise_exception=True)(AddSeviceView.as_view())),
    path("add-sub-factor/", permission_required('ticket.add_subfactor', raise_exception=True)(AddSubFactor.as_view())),
    path("get-services/", permission_required('ticket.view_service', raise_exception=True)(GetServiceData.as_view())),
    path("get-user-data/", permission_required('ticket.view_user', raise_exception=True)(GetUserData.as_view())),
    path("update-factor/", permission_required('ticket.change_factor', raise_exception=True)(UpdateFactorView.as_view())),
    path("update-sub-factor/", permission_required('ticket.change_subfactor', raise_exception=True)(UpdateSubFactorView.as_view())),
    path("view-factor/", permission_required('ticket.view_factor', raise_exception=True)(ViewFactorView.as_view())),
    path("view-profile/", permission_required('ticket.view_user', raise_exception=True)(ViewProfileView.as_view())),
    path("update-profile/", permission_required('ticket.change_user', raise_exception=True)(UpdateProfileView.as_view())),
    path("add-service-stylist/", permission_required('ticket.add_stylistservice', raise_exception=True)(AddServiceStylist.as_view())),
    path("view-customer/", permission_required('ticket.view_customer', raise_exception=True)(ViewCustomerView.as_view())),
    path("view-employ/", permission_required(['ticket.view_accountant', 'ticket.view_stylist'], raise_exception=True)(ViewEmployView.as_view())),
    path("", login_required(HomeView.as_view())),

]
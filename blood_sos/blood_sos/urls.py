from django.contrib import admin
from django.urls import path

from hemohub.views import (
    entry_page,
    login,
    register,
    forgot_password,
    reset_password,
    donor_dashboard,
    needer_dashboard,
    admin_dashboard,
    logout_user,
    create_request,cancel_request,check_password,my_requests,find_donor,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", entry_page, name="entry_page"),
    path("login/", login, name="login"),
    path("register/", register, name="register"),
    path("forgot-password/", forgot_password, name="forgot_password"),
    path("reset-password/", reset_password, name="reset_password"),

    path("donor-dashboard/", donor_dashboard, name="donor_dashboard"),
    path("needer-dashboard/", needer_dashboard, name="needer_dashboard"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("needer/dashboard/", needer_dashboard, name="needer_dashboard"),
    path("needer/create-request/", create_request, name="create_request"),
    path("needer/my-requests/", my_requests, name="my_requests"),
    path("needer/cancel/<int:request_id>/", cancel_request, name="cancel_request"),
    path("needer/find-donor/", find_donor, name="find_donor"),
    path("logout/", logout_user, name="logout"),
    path("logout/", logout_user, name="logout_user"),
]
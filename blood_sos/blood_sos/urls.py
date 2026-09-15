from django.contrib import admin
from django.urls import path

from hemohub.views import (
    entry_page,
    login,
    register,
    forgot_password,
    reset_password,

    # Dashboards
    donor_dashboard,
    needer_dashboard,
    admin_dashboard,

    # Donor
    donor_profile,
    update_availability,
    blood_radar,
    donor_requests,
    respond_to_request,
    donation_history,
    donor_alerts,

    # Needer
    create_request,
    cancel_request,
    my_requests,
    find_donor,

    # Other
    logout_user,
    check_password,
)


urlpatterns = [

    # =========================
    # ADMIN
    # =========================
    path("admin/", admin.site.urls),


    # =========================
    # AUTHENTICATION
    # =========================
    path("", entry_page, name="entry_page"),
    path("login/", login, name="login"),
    path("register/", register, name="register"),
    path("forgot-password/", forgot_password, name="forgot_password"),
    path("reset-password/", reset_password, name="reset_password"),
    path("check-password/", check_password, name="check_password"),


    # =========================
    # DASHBOARDS
    # =========================
    path(
        "donor-dashboard/",
        donor_dashboard,
        name="donor_dashboard"
    ),

    path(
        "needer-dashboard/",
        needer_dashboard,
        name="needer_dashboard"
    ),

    path(
        "admin-dashboard/",
        admin_dashboard,
        name="admin_dashboard"
    ),

    # Needer dashboard alternate URL
    path(
        "needer/dashboard/",
        needer_dashboard,
        name="needer_dashboard"
    ),


    # =========================
    # DONOR
    # =========================

    # Donor Profile
    path(
        "donor/profile/",
        donor_profile,
        name="donor_profile"
    ),

    # Donor availability
    path(
        "donor/update-availability/",
        update_availability,
        name="update_availability"
    ),

    # Blood Radar
    path(
        "donor/radar/",
        blood_radar,
        name="blood_radar"
    ),

    # Blood Requests
    path(
        "donor/requests/",
        donor_requests,
        name="donor_requests"
    ),

    # Respond to blood request
    path(
        "donor/respond/<int:request_id>/",
        respond_to_request,
        name="respond_to_request"
    ),

    # Donation History
    path(
        "donor/history/",
        donation_history,
        name="donation_history"
    ),

    # Donor Alerts
    path(
        "donor/alerts/",
        donor_alerts,
        name="donor_alerts"
    ),


    # =========================
    # NEEDER
    # =========================

    # Create Blood Request
    path(
        "needer/create-request/",
        create_request,
        name="create_request"
    ),

    # My Requests
    path(
        "needer/my-requests/",
        my_requests,
        name="my_requests"
    ),

    # Cancel Request
    path(
        "needer/cancel/<int:request_id>/",
        cancel_request,
        name="cancel_request"
    ),

    # Find Donor
    path(
        "needer/find-donor/",
        find_donor,
        name="find_donor"
    ),


    # =========================
    # LOGOUT
    # =========================
    path(
        "logout/",
        logout_user,
        name="logout_user"
    ),
]

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

    # Admin
    admin_users,
    admin_sos,
    admin_analytics,
    admin_verify_user,
    admin_block_user,
    admin_unblock_user,

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

    # =====================================================
    # DJANGO ADMIN
    # =====================================================

    path(
        "admin/",
        admin.site.urls
    ),


    # =====================================================
    # AUTHENTICATION
    # =====================================================

    path(
        "",
        entry_page,
        name="entry_page"
    ),

    path(
        "login/",
        login,
        name="login"
    ),

    path(
        "register/",
        register,
        name="register"
    ),

    path(
        "forgot-password/",
        forgot_password,
        name="forgot_password"
    ),

    path(
        "reset-password/",
        reset_password,
        name="reset_password"
    ),

    path(
        "check-password/",
        check_password,
        name="check_password"
    ),


    # =====================================================
    # DASHBOARDS
    # =====================================================

    # Donor Dashboard
    path(
        "donor-dashboard/",
        donor_dashboard,
        name="donor_dashboard"
    ),

    # Needer Dashboard
    path(
        "needer-dashboard/",
        needer_dashboard,
        name="needer_dashboard"
    ),

    # Admin Dashboard
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


    # =====================================================
    # ADMIN
    # =====================================================

    # Admin Users
    path(
        "admin/users/",
        admin_users,
        name="admin_users"
    ),

    # Admin SOS Monitoring
    path(
        "admin/sos/",
        admin_sos,
        name="admin_sos"
    ),

    # Admin Analytics
    path(
        "admin/analytics/",
        admin_analytics,
        name="admin_analytics"
    ),

    # Verify User
    path(
        "admin/users/<int:user_id>/verify/",
        admin_verify_user,
        name="admin_verify_user"
    ),

    # Block User
    path(
        "admin/users/<int:user_id>/block/",
        admin_block_user,
        name="admin_block_user"
    ),

    # Unblock User
    path(
        "admin/users/<int:user_id>/unblock/",
        admin_unblock_user,
        name="admin_unblock_user"
    ),


    # =====================================================
    # DONOR
    # =====================================================

    # Donor Profile
    path(
        "donor/profile/",
        donor_profile,
        name="donor_profile"
    ),

    # Donor Availability
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

    # Donor Blood Requests
    path(
        "donor/requests/",
        donor_requests,
        name="donor_requests"
    ),

    # Respond to Blood Request
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


    # =====================================================
    # NEEDER
    # =====================================================

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

    # Cancel Blood Request
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


    # =====================================================
    # LOGOUT
    # =====================================================

    path(
        "logout/",
        logout_user,
        name="logout_user"
    ),
]

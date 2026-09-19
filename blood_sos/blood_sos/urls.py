from django.contrib import admin
from django.urls import path

from hemohub.views import (

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    entry_page,
    login,
    register,
    forgot_password,
    reset_password,


    # =====================================================
    # DASHBOARDS
    # =====================================================

    donor_dashboard,
    needer_dashboard,
    admin_dashboard,


    # =====================================================
    # LOCATION
    # =====================================================

    save_location,


    # =====================================================
    # ADMIN
    # =====================================================

    admin_users,
    admin_sos,
    admin_analytics,
    admin_verify_user,
    admin_block_user,
    admin_unblock_user,


    # =====================================================
    # DONOR
    # =====================================================

    donor_profile,
    update_availability,
    blood_radar,
    donor_requests,
    respond_to_request,
    donation_history,
    donor_alerts,
    get_needer_donor_route,


    # =====================================================
    # NEEDER
    # =====================================================

    create_request,
    cancel_request,
    find_donor,

    # NEW: ROAD ROUTE API
    get_request_route,


    # =====================================================
    # OTHER
    # =====================================================

    logout_user,
)


urlpatterns = [


    # =====================================================
    # DJANGO BUILT-IN ADMIN
    # =====================================================

    path(
        "django-admin/",
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


    # =====================================================
    # DASHBOARDS
    # =====================================================

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


    # =====================================================
    # LOCATION
    # =====================================================

    path(
        "save-location/",
        save_location,
        name="save_location"
    ),


    # =====================================================
    # HEMOHUB ADMIN
    # =====================================================

    path(
        "admin/users/",
        admin_users,
        name="admin_users"
    ),

    path(
        "admin/sos/",
        admin_sos,
        name="admin_sos"
    ),

    path(
        "admin/analytics/",
        admin_analytics,
        name="admin_analytics"
    ),

    path(
        "admin/users/<int:user_id>/verify/",
        admin_verify_user,
        name="admin_verify_user"
    ),

    path(
        "admin/users/<int:user_id>/block/",
        admin_block_user,
        name="admin_block_user"
    ),

    path(
        "admin/users/<int:user_id>/unblock/",
        admin_unblock_user,
        name="admin_unblock_user"
    ),


    # =====================================================
    # DONOR
    # =====================================================

    path(
        "donor/profile/",
        donor_profile,
        name="donor_profile"
    ),

    path(
        "donor/update-availability/",
        update_availability,
        name="update_availability"
    ),

    path(
        "donor/radar/",
        blood_radar,
        name="blood_radar"
    ),

    path(
        "donor/requests/",
        donor_requests,
        name="donor_requests"
    ),

    path(
        "donor/respond/<int:request_id>/",
        respond_to_request,
        name="respond_to_request"
    ),

    path(
        "donor/history/",
        donation_history,
        name="donation_history"
    ),

    path(
        "donor/alerts/",
        donor_alerts,
        name="donor_alerts"
    ),


    # =====================================================
    # ROAD ROUTE
    # =====================================================

    path(
        "request-route/<int:request_id>/",
        get_request_route,
        name="get_request_route"
    ),


    # =====================================================
    # NEEDER
    # =====================================================

    path(
        "needer-dashboard/",
        needer_dashboard,
        name="needer_dashboard"
    ),

    path(
        "needer/create-request/",
        create_request,
        name="create_request"
    ),

    path(
        "needer/cancel/<int:request_id>/",
        cancel_request,
        name="cancel_request"
    ),

    path(
        "needer/find-donor/",
        find_donor,
        name="find_donor"
    ),
    path(
        "needer/donor-route/<int:response_id>/",
        get_needer_donor_route,
        name="get_needer_donor_route"
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
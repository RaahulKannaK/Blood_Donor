from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from math import radians, sin, cos, sqrt, atan2

from .models import (
    LoginUser,
    DonorProfile,
    BloodRequest,
    DonorResponse,
    DonationHistory
)


# ============================================================
# ENTRY PAGE
# ============================================================

def entry_page(request):
    return render(
        request,
        "entry.html"
    )


# ============================================================
# LOGIN
# ============================================================

def login(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        ).strip()

        password = request.POST.get(
            "password"
        ).strip()

        try:
            user = LoginUser.objects.get(
                username=username,
                password=password
            )

            request.session["user_id"] = user.id
            request.session["username"] = user.username
            request.session["role"] = user.role

            if user.role == "donor":
                return redirect(
                    "donor_dashboard"
                )

            elif user.role == "needer":
                return redirect(
                    "needer_dashboard"
                )

            elif user.role == "admin":
                return redirect(
                    "admin_dashboard"
                )

        except LoginUser.DoesNotExist:

            messages.error(
                request,
                "Invalid username or password."
            )

    return render(
        request,
        "login.html"
    )


# ============================================================
# REGISTER
# ============================================================

def register(request):

    if request.method == "POST":

        name = request.POST.get(
            "name"
        ).strip()

        username = request.POST.get(
            "username"
        ).strip()

        email = request.POST.get(
            "email"
        ).strip()

        password = request.POST.get(
            "password"
        ).strip()

        role = request.POST.get(
            "role"
        ).strip()

        age = request.POST.get(
            "age"
        ).strip()

        if LoginUser.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect(
                "register"
            )

        LoginUser.objects.create(
            name=name,
            username=username,
            email=email,
            password=password,
            role=role,
            age=age
        )

        messages.success(
            request,
            "Registration successful. Please login."
        )

        return redirect(
            "login"
        )

    return render(
        request,
        "register.html"
    )


# ============================================================
# FORGOT PASSWORD
# ============================================================

def forgot_password(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        ).strip()

        email = request.POST.get(
            "email"
        ).strip()

        try:

            user = LoginUser.objects.get(
                username=username,
                email=email
            )

            request.session[
                "reset_user_id"
            ] = user.id

            return redirect(
                "reset_password"
            )

        except LoginUser.DoesNotExist:

            messages.error(
                request,
                "Username and email do not match."
            )

    return render(
        request,
        "forgot_password.html"
    )


# ============================================================
# RESET PASSWORD
# ============================================================

def reset_password(request):

    if "reset_user_id" not in request.session:
        return redirect(
            "forgot_password"
        )

    if request.method == "POST":

        password = request.POST.get(
            "password"
        ).strip()

        confirm_password = request.POST.get(
            "confirm_password"
        ).strip()

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect(
                "reset_password"
            )

        user_id = request.session.get(
            "reset_user_id"
        )

        try:

            user = LoginUser.objects.get(
                id=user_id
            )

            user.password = password
            user.save()

            del request.session[
                "reset_user_id"
            ]

            messages.success(
                request,
                "Password reset successfully."
            )

            return redirect(
                "login"
            )

        except LoginUser.DoesNotExist:

            return redirect(
                "forgot_password"
            )

    return render(
        request,
        "reset_password.html"
    )


# ============================================================
# DONOR DASHBOARD
# ============================================================

def donor_dashboard(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="donor"
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    try:

        donor = DonorProfile.objects.get(
            user=user
        )

    except DonorProfile.DoesNotExist:

        donor = None

    response_count = DonorResponse.objects.filter(
        donor=donor
    ).count() if donor else 0

    donation_count = DonationHistory.objects.filter(
        donor=donor
    ).count() if donor else 0

    context = {
        "name": user.name,
        "username": user.username,
        "age": user.age,
        "role": user.role,
        "donor": donor,
        "response_count": response_count,
        "donation_count": donation_count,
    }

    return render(
        request,
        "donor/donor_dashboard.html",
        context
    )


# ============================================================
# DONOR PROFILE
# ============================================================

def donor_profile(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="donor"
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    donor, created = DonorProfile.objects.get_or_create(
        user=user
    )

    if request.method == "POST":

        donor.blood_group = request.POST.get(
            "blood_group",
            donor.blood_group
        )

        donor.phone = request.POST.get(
            "phone",
            donor.phone
        )

        donor.gender = request.POST.get(
            "gender",
            donor.gender
        )

        donor.address = request.POST.get(
            "address",
            donor.address
        )

        donor.save()

        user.name = request.POST.get(
            "name",
            user.name
        )

        user.age = request.POST.get(
            "age",
            user.age
        )

        user.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect(
            "donor_profile"
        )

    context = {
        "user": user,
        "donor": donor,
        "name": user.name,
        "username": user.username,
        "age": user.age,
    }

    return render(
        request,
        "donor/donor_profile.html",
        context
    )


# ============================================================
# UPDATE DONOR AVAILABILITY
# ============================================================

def update_availability(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="donor"
        )

        donor = DonorProfile.objects.get(
            user=user
        )

    except (
        LoginUser.DoesNotExist,
        DonorProfile.DoesNotExist
    ):

        return redirect(
            "login"
        )

    if request.method == "POST":

        availability = request.POST.get(
            "availability"
        )

        donor.availability = availability
        donor.save()

        messages.success(
            request,
            "Availability updated successfully."
        )

    return redirect(
        "donor_dashboard"
    )


# ============================================================
# SAVE LOCATION
# ============================================================

def save_location(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    latitude = request.POST.get(
        "latitude"
    )

    longitude = request.POST.get(
        "longitude"
    )

    if not latitude or not longitude:

        return JsonResponse({
            "success": False,
            "message": "Location data missing."
        })

    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )

    except (
        ValueError,
        TypeError
    ):

        return JsonResponse({
            "success": False,
            "message": "Invalid location data."
        })

    if user.role == "donor":

        try:

            donor = DonorProfile.objects.get(
                user=user
            )

            donor.latitude = latitude
            donor.longitude = longitude
            donor.save()

        except DonorProfile.DoesNotExist:

            return JsonResponse({
                "success": False,
                "message": "Donor profile not found."
            })

    elif user.role == "needer":

        active_request = BloodRequest.objects.filter(
            needer=user,
            status="Active"
        ).order_by(
            "-created_at"
        ).first()

        if active_request:

            active_request.latitude = latitude
            active_request.longitude = longitude
            active_request.save()

    return JsonResponse({
        "success": True,
        "message": "Location saved successfully."
    })


# ============================================================
# CALCULATE DISTANCE
# ============================================================

def calculate_distance_km(
    lat1,
    lon1,
    lat2,
    lon2
):

    if (
        lat1 is None
        or lon1 is None
        or lat2 is None
        or lon2 is None
    ):
        return None

    try:

        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)

    except (
        ValueError,
        TypeError
    ):

        return None

    earth_radius = 6371

    dlat = radians(
        lat2 - lat1
    )

    dlon = radians(
        lon2 - lon1
    )

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius * c


# ============================================================
# BLOOD RADAR
# ============================================================

def blood_radar(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="donor"
        )

        donor = DonorProfile.objects.get(
            user=user
        )

    except (
        LoginUser.DoesNotExist,
        DonorProfile.DoesNotExist
    ):

        return redirect(
            "login"
        )

    blood_requests = BloodRequest.objects.filter(
        status="Active"
    ).exclude(
        needer=user
    ).order_by(
        "-created_at"
    )

    for blood_request in blood_requests:

        blood_request.distance_km = calculate_distance_km(
            donor.latitude,
            donor.longitude,
            blood_request.latitude,
            blood_request.longitude
        )

    context = {
        "name": user.name,
        "username": user.username,
        "donor": donor,
        "blood_requests": blood_requests,
    }

    return render(
        request,
        "donor/blood_radar.html",
        context
    )


# ============================================================
# DONOR REQUESTS
# ============================================================

def donor_requests(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="donor"
        )

        donor = DonorProfile.objects.get(
            user=user
        )

    except (
        LoginUser.DoesNotExist,
        DonorProfile.DoesNotExist
    ):

        return redirect(
            "login"
        )

    responses = DonorResponse.objects.filter(
        donor=donor
    ).select_related(
        "blood_request",
        "blood_request__needer"
    ).order_by(
        "-created_at"
    )

    context = {
        "name": user.name,
        "username": user.username,
        "donor": donor,
        "responses": responses,
    }

    return render(
        request,
        "donor/donor_requests.html",
        context
    )


# ============================================================
# RESPOND TO BLOOD REQUEST
# ============================================================

def respond_to_request(
    request,
    request_id
):

    if "user_id" not in request.session:
        return redirect("login")

    if request.method != "POST":

        return redirect(
            "donor_requests"
        )

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="donor"
        )

        donor = DonorProfile.objects.get(
            user=user
        )

        blood_request = BloodRequest.objects.get(
            id=request_id,
            status="Active"
        )

    except (
        LoginUser.DoesNotExist,
        DonorProfile.DoesNotExist,
        BloodRequest.DoesNotExist
    ):

        messages.error(
            request,
            "Blood request not found."
        )

        return redirect(
            "donor_requests"
        )

    existing_response = DonorResponse.objects.filter(
        donor=donor,
        blood_request=blood_request
    ).first()

    if existing_response:

        messages.info(
            request,
            "You have already responded to this request."
        )

        return redirect(
            "donor_requests"
        )

    DonorResponse.objects.create(
        donor=donor,
        blood_request=blood_request,
        status="Responded"
    )

    messages.success(
        request,
        "Response sent successfully."
    )

    return redirect(
        "donor_requests"
    )


# ============================================================
# DONATION HISTORY
# ============================================================

def donation_history(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="donor"
        )

        donor = DonorProfile.objects.get(
            user=user
        )

    except (
        LoginUser.DoesNotExist,
        DonorProfile.DoesNotExist
    ):

        return redirect(
            "login"
        )

    history = DonationHistory.objects.filter(
        donor=donor
    ).order_by(
        "-donation_date"
    )

    context = {
        "name": user.name,
        "username": user.username,
        "donor": donor,
        "history": history,
    }

    return render(
        request,
        "donor/donation_history.html",
        context
    )


# ============================================================
# DONOR ALERTS
# ============================================================

def donor_alerts(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="donor"
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    alerts = BloodRequest.objects.filter(
        status="Active"
    ).order_by(
        "-created_at"
    )

    context = {
        "name": user.name,
        "username": user.username,
        "alerts": alerts,
    }

    return render(
        request,
        "donor/alerts.html",
        context
    )


# ============================================================
# NEEDER DASHBOARD
# ============================================================

def needer_dashboard(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="needer"
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    active_requests = BloodRequest.objects.filter(
        needer=user,
        status="Active"
    )

    fulfilled_requests = BloodRequest.objects.filter(
        needer=user,
        status="Fulfilled"
    )

    response_count = DonorResponse.objects.filter(
        blood_request__needer=user
    ).count()

    active_count = active_requests.count()
    fulfilled_count = fulfilled_requests.count()

    active_request = active_requests.order_by(
        "-created_at"
    ).first()

    progress = 0

    if active_request:

        total_units = active_request.units or 0

        accepted_responses = DonorResponse.objects.filter(
            blood_request=active_request,
            status__in=[
                "Accepted",
                "Completed"
            ]
        ).count()

        if total_units > 0:

            progress = min(
                100,
                int(
                    accepted_responses
                    / total_units
                    * 100
                )
            )

    context = {
        "name": user.name,
        "username": user.username,
        "age": user.age,
        "role": user.role,
        "active_count": active_count,
        "fulfilled_count": fulfilled_count,
        "response_count": response_count,
        "active_request": active_request,
        "progress": progress,
    }

    return render(
        request,
        "needer/needer_dahboard.html",
        context
    )


# ============================================================
# CREATE REQUEST + MY REQUESTS
# ============================================================

def create_request(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="needer"
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    if request.method == "POST":

        blood_group = request.POST.get(
            "bloodGroup",
            request.POST.get(
                "blood_group",
                ""
            )
        ).strip()

        patient_name = request.POST.get(
            "patientName",
            request.POST.get(
                "patient_name",
                ""
            )
        ).strip()

        patient_age = request.POST.get(
            "patientAge",
            request.POST.get(
                "patient_age",
                ""
            )
        ).strip()

        units = request.POST.get(
            "units",
            ""
        ).strip()

        hospital = request.POST.get(
            "hospital",
            ""
        ).strip()

        location = request.POST.get(
            "location",
            ""
        ).strip()

        urgency = request.POST.get(
            "urgency",
            "Normal"
        ).strip()

        additional_info = request.POST.get(
            "additionalInfo",
            request.POST.get(
                "additional_info",
                ""
            )
        ).strip()

        latitude = request.POST.get(
            "latitude",
            ""
        ).strip()

        longitude = request.POST.get(
            "longitude",
            ""
        ).strip()

        if not all([
            blood_group,
            patient_name,
            patient_age,
            units,
            hospital,
            location,
            urgency
        ]):

            messages.error(
                request,
                "Please fill all required fields."
            )

            return redirect(
                "create_request"
            )

        try:

            patient_age_value = int(
                patient_age
            )

            if patient_age_value <= 0:
                raise ValueError

        except (
            ValueError,
            TypeError
        ):

            messages.error(
                request,
                "Patient age must be a valid number."
            )

            return redirect(
                "create_request"
            )

        try:

            units_value = int(
                units
            )

            if units_value <= 0:
                raise ValueError

        except (
            ValueError,
            TypeError
        ):

            messages.error(
                request,
                "Blood units must be a valid number."
            )

            return redirect(
                "create_request"
            )

        latitude_value = None
        longitude_value = None

        if latitude:

            try:

                latitude_value = float(
                    latitude
                )

                if not -90 <= latitude_value <= 90:
                    latitude_value = None

            except (
                ValueError,
                TypeError
            ):

                latitude_value = None

        if longitude:

            try:

                longitude_value = float(
                    longitude
                )

                if not -180 <= longitude_value <= 180:
                    longitude_value = None

            except (
                ValueError,
                TypeError
            ):

                longitude_value = None

        BloodRequest.objects.create(
            needer=user,
            blood_group=blood_group,
            patient_name=patient_name,
            patient_age=patient_age_value,
            units=units_value,
            hospital=hospital,
            location=location,
            urgency=urgency,
            additional_info=additional_info,
            latitude=latitude_value,
            longitude=longitude_value,
            status="Active"
        )

        messages.success(
            request,
            "Blood request created successfully."
        )

        return redirect(
            "create_request"
        )

    requests_list = BloodRequest.objects.filter(
        needer=user
    ).order_by(
        "-created_at"
    )

    for blood_request in requests_list:

        blood_request.response_count = (
            DonorResponse.objects.filter(
                blood_request=blood_request
            ).count()
        )

    latest_request = requests_list.first()

    donor_responses = []
    response_count = 0

    if latest_request:

        donor_responses = DonorResponse.objects.filter(
            blood_request=latest_request
        ).select_related(
            "donor",
            "donor__user"
        ).order_by(
            "-created_at"
        )

        response_count = donor_responses.count()

        for response in donor_responses:

            donor = response.donor

            distance = calculate_distance_km(
                latest_request.latitude,
                latest_request.longitude,
                donor.latitude,
                donor.longitude
            )

            response.distance_km = (
                round(
                    distance,
                    2
                )
                if distance is not None
                else None
            )

            response.location_available = (
                donor.latitude is not None
                and donor.longitude is not None
            )

    context = {
        "name": user.name,
        "username": user.username,
        "age": user.age,
        "requests_list": requests_list,
        "latest_request": latest_request,
        "donor_responses": donor_responses,
        "response_count": response_count,
    }

    return render(
        request,
        "needer/create_request.html",
        context
    )


# ============================================================
# CANCEL BLOOD REQUEST
# ============================================================

def cancel_request(
    request,
    request_id
):

    if "user_id" not in request.session:
        return redirect("login")

    if request.method != "POST":

        return redirect(
            "create_request"
        )

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="needer"
        )

        blood_request = BloodRequest.objects.get(
            id=request_id,
            needer=user
        )

    except (
        LoginUser.DoesNotExist,
        BloodRequest.DoesNotExist
    ):

        messages.error(
            request,
            "Blood request not found."
        )

        return redirect(
            "create_request"
        )

    blood_request.status = "Cancelled"
    blood_request.save()

    messages.success(
        request,
        "Blood request cancelled successfully."
    )

    return redirect(
        "create_request"
    )


# ============================================================
# FIND DONOR
# ============================================================

def find_donor(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="needer"
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    requests_list = BloodRequest.objects.filter(
        needer=user
    ).order_by(
        "-created_at"
    )

    for blood_request in requests_list:

        blood_request.response_count = (
            DonorResponse.objects.filter(
                blood_request=blood_request
            ).count()
        )

    selected_request = None

    request_id = request.GET.get(
        "request_id"
    )

    if request_id:

        try:

            selected_request = BloodRequest.objects.get(
                id=request_id,
                needer=user
            )

        except (
            BloodRequest.DoesNotExist,
            ValueError,
            TypeError
        ):

            selected_request = None

    donor_responses = []

    response_count = 0
    accepted_count = 0
    pending_count = 0
    rejected_count = 0
    completed_count = 0

    if selected_request:

        donor_responses = DonorResponse.objects.filter(
            blood_request=selected_request
        ).select_related(
            "donor",
            "donor__user"
        ).order_by(
            "-created_at"
        )

        response_count = donor_responses.count()

        accepted_count = donor_responses.filter(
            status="Accepted"
        ).count()

        pending_count = donor_responses.filter(
            status__in=[
                "Responded",
                "Pending"
            ]
        ).count()

        rejected_count = donor_responses.filter(
            status="Rejected"
        ).count()

        completed_count = donor_responses.filter(
            status="Completed"
        ).count()

        for response in donor_responses:

            donor = response.donor

            distance = calculate_distance_km(
                selected_request.latitude,
                selected_request.longitude,
                donor.latitude,
                donor.longitude
            )

            response.distance_km = (
                round(
                    distance,
                    2
                )
                if distance is not None
                else None
            )

            response.location_available = (
                donor.latitude is not None
                and donor.longitude is not None
            )

    context = {
        "name": user.name,
        "username": user.username,
        "age": user.age,
        "requests_list": requests_list,
        "selected_request": selected_request,
        "donor_responses": donor_responses,
        "response_count": response_count,
        "accepted_count": accepted_count,
        "pending_count": pending_count,
        "rejected_count": rejected_count,
        "completed_count": completed_count,
    }

    return render(
        request,
        "needer/find_donor.html",
        context
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

def admin_dashboard(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        user = LoginUser.objects.get(
            id=user_id,
            role="admin"
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    total_users = LoginUser.objects.count()

    total_donors = LoginUser.objects.filter(
        role="donor"
    ).count()

    total_needers = LoginUser.objects.filter(
        role="needer"
    ).count()

    total_requests = BloodRequest.objects.count()

    active_requests = BloodRequest.objects.filter(
        status="Active"
    ).count()

    fulfilled_requests = BloodRequest.objects.filter(
        status="Fulfilled"
    ).count()

    context = {
        "name": user.name,
        "username": user.username,
        "total_users": total_users,
        "total_donors": total_donors,
        "total_needers": total_needers,
        "total_requests": total_requests,
        "active_requests": active_requests,
        "fulfilled_requests": fulfilled_requests,
    }

    return render(
        request,
        "admin/admin_dashboard.html",
        context
    )


# ============================================================
# ADMIN USERS
# ============================================================

def admin_users(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get(
        "user_id"
    )

    try:

        admin = LoginUser.objects.get(
            id=user_id,
            role="admin"
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    users = LoginUser.objects.exclude(
        role="admin"
    ).order_by(
        "-id"
    )

    context = {
        "name": admin.name,
        "username": admin.username,
        "users": users,
    }

    return render(
        request,
        "admin/users.html",
        context
    )


# ============================================================
# ADMIN VERIFY USER
# ============================================================

def admin_verify_user(
    request,
    user_id
):

    if "user_id" not in request.session:
        return redirect("login")

    try:

        admin = LoginUser.objects.get(
            id=request.session.get("user_id"),
            role="admin"
        )

        user = LoginUser.objects.get(
            id=user_id
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    user.is_verified = True
    user.save()

    messages.success(
        request,
        "User verified successfully."
    )

    return redirect(
        "admin_users"
    )


# ============================================================
# ADMIN BLOCK USER
# ============================================================

def admin_block_user(
    request,
    user_id
):

    if "user_id" not in request.session:
        return redirect("login")

    try:

        LoginUser.objects.get(
            id=request.session.get("user_id"),
            role="admin"
        )

        user = LoginUser.objects.get(
            id=user_id
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    user.is_blocked = True
    user.save()

    messages.success(
        request,
        "User blocked successfully."
    )

    return redirect(
        "admin_users"
    )


# ============================================================
# ADMIN UNBLOCK USER
# ============================================================

def admin_unblock_user(
    request,
    user_id
):

    if "user_id" not in request.session:
        return redirect("login")

    try:

        LoginUser.objects.get(
            id=request.session.get("user_id"),
            role="admin"
        )

        user = LoginUser.objects.get(
            id=user_id
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    user.is_blocked = False
    user.save()

    messages.success(
        request,
        "User unblocked successfully."
    )

    return redirect(
        "admin_users"
    )


# ============================================================
# ADMIN SOS
# ============================================================

def admin_sos(request):

    if "user_id" not in request.session:
        return redirect("login")

    try:

        admin = LoginUser.objects.get(
            id=request.session.get("user_id"),
            role="admin"
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    sos_requests = BloodRequest.objects.filter(
        urgency="Emergency",
        status="Active"
    ).order_by(
        "-created_at"
    )

    context = {
        "name": admin.name,
        "username": admin.username,
        "sos_requests": sos_requests,
    }

    return render(
        request,
        "admin/sos.html",
        context
    )


# ============================================================
# ADMIN ANALYTICS
# ============================================================

def admin_analytics(request):

    if "user_id" not in request.session:
        return redirect("login")

    try:

        admin = LoginUser.objects.get(
            id=request.session.get("user_id"),
            role="admin"
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "login"
        )

    total_donors = LoginUser.objects.filter(
        role="donor"
    ).count()

    total_needers = LoginUser.objects.filter(
        role="needer"
    ).count()

    total_requests = BloodRequest.objects.count()

    fulfilled_requests = BloodRequest.objects.filter(
        status="Fulfilled"
    ).count()

    context = {
        "name": admin.name,
        "username": admin.username,
        "total_donors": total_donors,
        "total_needers": total_needers,
        "total_requests": total_requests,
        "fulfilled_requests": fulfilled_requests,
    }

    return render(
        request,
        "admin/analytics.html",
        context
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_user(request):

    request.session.flush()

    return redirect(
        "login"
    )
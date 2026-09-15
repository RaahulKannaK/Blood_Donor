from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta

from .models import (
    LoginUser,
    DonorProfile,
    BloodRequest,
    DonorResponse,
    DonationHistory,
    Hospital
)


# =========================================================
# ENTRY PAGE
# =========================================================

def entry_page(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        if not name or not password:

            messages.error(
                request,
                "Please enter your name and password."
            )

            return render(
                request,
                "hemohub/entry.html"
            )

        try:

            user = LoginUser.objects.get(
                name__iexact=name
            )

        except LoginUser.DoesNotExist:

            messages.error(
                request,
                "Name or password is incorrect."
            )

            return render(
                request,
                "hemohub/entry.html"
            )

        if user.is_blocked:

            messages.error(
                request,
                "Your account has been blocked by Admin."
            )

            return render(
                request,
                "hemohub/entry.html"
            )

        if check_password(
            password,
            user.password
        ):

            request.session["person_id"] = user.id
            request.session["person_name"] = user.name

            return redirect("login")

        messages.error(
            request,
            "Name or password is incorrect."
        )

    return render(
        request,
        "hemohub/entry.html"
    )


# =========================================================
# LOGIN
# =========================================================

def login(request):

    if "person_id" not in request.session:

        return redirect("entry_page")

    person_name = request.session.get(
        "person_name"
    )

    if request.method == "POST":

        role = request.POST.get(
            "role",
            ""
        ).strip()

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        if not role:

            messages.error(
                request,
                "Please select a role."
            )

            return render(
                request,
                "hemohub/login.html",
                {
                    "person_name": person_name
                }
            )

        if not username or not password:

            messages.error(
                request,
                "Please enter username and password."
            )

            return render(
                request,
                "hemohub/login.html",
                {
                    "person_name": person_name
                }
            )

        try:

            user = LoginUser.objects.get(
                username__iexact=username,
                role=role
            )

        except LoginUser.DoesNotExist:

            messages.error(
                request,
                "Invalid username, password or role."
            )

            return render(
                request,
                "hemohub/login.html",
                {
                    "person_name": person_name
                }
            )

        if user.is_blocked:

            messages.error(
                request,
                "This account has been blocked by Admin."
            )

            return render(
                request,
                "hemohub/login.html",
                {
                    "person_name": person_name
                }
            )

        if not check_password(
            password,
            user.password
        ):

            messages.error(
                request,
                "Invalid username, password or role."
            )

            return render(
                request,
                "hemohub/login.html",
                {
                    "person_name": person_name
                }
            )

        # -------------------------------------------------
        # LOGIN SUCCESS
        # -------------------------------------------------

        request.session["user_id"] = user.id
        request.session["username"] = user.username
        request.session["role"] = user.role
        request.session["name"] = user.name

        request.session.pop(
            "person_id",
            None
        )

        request.session.pop(
            "person_name",
            None
        )

        if user.role == "admin":

            return redirect(
                "admin_dashboard"
            )

        elif user.role == "donor":

            DonorProfile.objects.get_or_create(
                user=user,
                defaults={
                    "blood_group": "",
                    "location": "",
                    "phone": "",
                    "is_available": True
                }
            )

            return redirect(
                "donor_dashboard"
            )

        elif user.role == "needer":

            return redirect(
                "needer_dashboard"
            )

    return render(
        request,
        "hemohub/login.html",
        {
            "person_name": person_name
        }
    )


# =========================================================
# REGISTER
# =========================================================

def register(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        age = request.POST.get(
            "age",
            ""
        )

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        role = request.POST.get(
            "role",
            ""
        ).strip()

        if not all([
            name,
            age,
            username,
            password,
            confirm_password,
            role
        ]):

            messages.error(
                request,
                "Please fill all fields."
            )

            return render(
                request,
                "hemohub/register.html"
            )

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "hemohub/register.html"
            )

        if LoginUser.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return render(
                request,
                "hemohub/register.html"
            )

        user = LoginUser.objects.create(
            name=name,
            age=age,
            username=username,
            password=make_password(password),
            role=role,

            # Admin accounts are automatically verified.
            is_verified=(role == "admin"),

            is_blocked=False
        )

        if role == "donor":

            DonorProfile.objects.create(
                user=user,
                blood_group="",
                location="",
                phone="",
                is_available=True
            )

        messages.success(
            request,
            "Registration successful. Please login."
        )

        return redirect(
            "entry_page"
        )

    return render(
        request,
        "hemohub/register.html"
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================

def forgot_password(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        if not username:

            messages.error(
                request,
                "Please enter your username."
            )

            return render(
                request,
                "hemohub/forgot_password.html"
            )

        try:

            user = LoginUser.objects.get(
                username__iexact=username
            )

        except LoginUser.DoesNotExist:

            messages.error(
                request,
                "Username not found."
            )

            return render(
                request,
                "hemohub/forgot_password.html"
            )

        request.session["reset_user_id"] = user.id

        return redirect(
            "reset_password"
        )

    return render(
        request,
        "hemohub/forgot_password.html"
    )


# =========================================================
# RESET PASSWORD
# =========================================================

def reset_password(request):

    user_id = request.session.get(
        "reset_user_id"
    )

    if not user_id:

        return redirect(
            "forgot_password"
        )

    try:

        user = LoginUser.objects.get(
            id=user_id
        )

    except LoginUser.DoesNotExist:

        return redirect(
            "forgot_password"
        )

    if request.method == "POST":

        new_password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        if not new_password or not confirm_password:

            messages.error(
                request,
                "Please enter both passwords."
            )

            return render(
                request,
                "hemohub/reset_password.html"
            )

        if new_password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "hemohub/reset_password.html"
            )

        user.password = make_password(
            new_password
        )

        user.save()

        request.session.pop(
            "reset_user_id",
            None
        )

        messages.success(
            request,
            "Password changed successfully."
        )

        return redirect(
            "entry_page"
        )

    return render(
        request,
        "hemohub/reset_password.html"
    )


# =========================================================
# DONOR DASHBOARD
# =========================================================

def donor_dashboard(request):

    if request.session.get("role") != "donor":

        return redirect("entry_page")

    user_id = request.session.get(
        "user_id"
    )

    try:

        donor = DonorProfile.objects.select_related(
            "user"
        ).get(
            user_id=user_id
        )

    except DonorProfile.DoesNotExist:

        messages.error(
            request,
            "Donor profile not found."
        )

        return redirect(
            "entry_page"
        )

    nearby_requests = BloodRequest.objects.filter(
        status="Active",
        blood_group=donor.blood_group
    ).order_by(
        "-created_at"
    )

    nearby_count = nearby_requests.count()

    donation_history = DonationHistory.objects.filter(
        donor=donor
    ).order_by(
        "-donation_date"
    )

    total_donations = donation_history.count()

    lives_helped = total_donations * 3

    context = {

        "donor": donor,

        "name": donor.user.name,

        "username": donor.user.username,

        "age": donor.user.age,

        "blood_group": donor.blood_group,

        "location": donor.location,

        "phone": donor.phone,

        "is_available": donor.is_available,

        "nearby_requests": nearby_requests,

        "nearby_count": nearby_count,

        "total_donations": total_donations,

        "lives_helped": lives_helped,

        "last_donation": donation_history.first(),

    }

    return render(
        request,
        "donor/dashboard.html",
        context
    )


# =========================================================
# DONOR PROFILE
# =========================================================

def donor_profile(request):

    if request.session.get("role") != "donor":

        return redirect("entry_page")

    user_id = request.session.get(
        "user_id"
    )

    try:

        donor = DonorProfile.objects.select_related(
            "user"
        ).get(
            user_id=user_id
        )

    except DonorProfile.DoesNotExist:

        return redirect(
            "donor_dashboard"
        )

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        age = request.POST.get(
            "age",
            ""
        )

        blood_group = request.POST.get(
            "blood",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        location = request.POST.get(
            "city",
            ""
        ).strip()

        last_donation = request.POST.get(
            "lastDonation",
            ""
        )

        if name:
            donor.user.name = name

        if age:
            donor.user.age = age

        donor.user.save()

        if blood_group:
            donor.blood_group = blood_group

        donor.phone = phone
        donor.location = location

        if last_donation:

            donor.last_donation_date = last_donation

        else:

            donor.last_donation_date = None

        donor.save()

        request.session["name"] = donor.user.name

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect(
            "donor_profile"
        )

    context = {

        "donor": donor,

        "name": donor.user.name,

        "age": donor.user.age,

        "username": donor.user.username,

        "blood_group": donor.blood_group,

        "phone": donor.phone,

        "location": donor.location,

        "last_donation_date":
            donor.last_donation_date,

        "is_available":
            donor.is_available,

    }

    return render(
        request,
        "donor/profile.html",
        context
    )


# =========================================================
# DONOR AVAILABILITY
# =========================================================

def update_availability(request):

    if request.session.get("role") != "donor":

        return redirect("entry_page")

    user_id = request.session.get(
        "user_id"
    )

    try:

        donor = DonorProfile.objects.get(
            user_id=user_id
        )

    except DonorProfile.DoesNotExist:

        return redirect(
            "donor_dashboard"
        )

    if request.method == "POST":

        availability = request.POST.get(
            "availability"
        )

        donor.is_available = (
            availability == "on"
        )

        donor.save()

        if donor.is_available:

            messages.success(
                request,
                "You are now available for blood donation."
            )

        else:

            messages.success(
                request,
                "You are now unavailable for blood donation."
            )

    return redirect(
        "donor_dashboard"
    )


# =========================================================
# BLOOD RADAR
# =========================================================

def blood_radar(request):

    if request.session.get("role") != "donor":

        return redirect("entry_page")

    user_id = request.session.get(
        "user_id"
    )

    donor = DonorProfile.objects.get(
        user_id=user_id
    )

    blood_group = request.GET.get(
        "blood_group",
        "all"
    )

    radius = request.GET.get(
        "radius",
        "all"
    )

    requests_list = BloodRequest.objects.filter(
        status="Active"
    ).order_by(
        "-created_at"
    )

    if blood_group != "all":

        requests_list = requests_list.filter(
            blood_group=blood_group
        )

    elif donor.blood_group:

        requests_list = requests_list.filter(
            blood_group=donor.blood_group
        )

    if radius != "all":

        try:

            radius_value = float(radius)

            requests_list = requests_list.filter(
                needer__isnull=False
            )

            # Distance filtering can be implemented
            # after adding request coordinates.

        except ValueError:

            pass

    return render(
        request,
        "donor/radar.html",
        {
            "donor": donor,
            "requests_list": requests_list,
            "blood_group": blood_group,
            "radius": radius
        }
    )


# =========================================================
# DONOR REQUESTS
# =========================================================

def donor_requests(request):

    if request.session.get("role") != "donor":

        return redirect("entry_page")

    user_id = request.session.get(
        "user_id"
    )

    donor = DonorProfile.objects.get(
        user_id=user_id
    )

    status_filter = request.GET.get(
        "status",
        "all"
    )

    requests_list = BloodRequest.objects.filter(
        status="Active"
    ).order_by(
        "-created_at"
    )

    if donor.blood_group:

        requests_list = requests_list.filter(
            blood_group=donor.blood_group
        )

    if status_filter != "all":

        status_map = {

            "critical": "Emergency",

            "urgent": "Urgent",

            "normal": "Normal",

        }

        if status_filter in status_map:

            requests_list = requests_list.filter(
                urgency=status_map[status_filter]
            )

    responses = DonorResponse.objects.filter(
        donor=donor
    )

    responded_request_ids = responses.values_list(
        "blood_request_id",
        flat=True
    )

    context = {

        "donor": donor,

        "requests_list": requests_list,

        "status_filter": status_filter,

        "responded_request_ids":
            responded_request_ids,

    }

    return render(
        request,
        "donor/requests.html",
        context
    )


# =========================================================
# RESPOND TO REQUEST
# =========================================================

def respond_to_request(
    request,
    request_id
):

    if request.session.get("role") != "donor":

        return redirect("entry_page")

    user_id = request.session.get(
        "user_id"
    )

    try:

        donor = DonorProfile.objects.get(
            user_id=user_id
        )

    except DonorProfile.DoesNotExist:

        return redirect(
            "donor_dashboard"
        )

    try:

        blood_request = BloodRequest.objects.get(
            id=request_id,
            status="Active"
        )

    except BloodRequest.DoesNotExist:

        messages.error(
            request,
            "Blood request not found or no longer active."
        )

        return redirect(
            "donor_requests"
        )

    if not donor.is_available:

        messages.error(
            request,
            "You are currently unavailable for donation."
        )

        return redirect(
            "donor_requests"
        )

    if donor.blood_group != blood_request.blood_group:

        messages.error(
            request,
            "Your blood group does not match this request."
        )

        return redirect(
            "donor_requests"
        )

    already_responded = DonorResponse.objects.filter(
        donor=donor,
        blood_request=blood_request
    ).exists()

    if already_responded:

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
        "Thank you! Your response has been sent successfully."
    )

    return redirect(
        "donor_requests"
    )


# =========================================================
# DONATION HISTORY
# =========================================================

def donation_history(request):

    if request.session.get("role") != "donor":

        return redirect("entry_page")

    donor = DonorProfile.objects.get(
        user_id=request.session["user_id"]
    )

    history = DonationHistory.objects.filter(
        donor=donor
    ).order_by(
        "-donation_date"
    )

    total_donations = history.count()

    lives_helped = total_donations * 3

    return render(
        request,
        "donor/history.html",
        {
            "donor": donor,
            "history": history,
            "total_donations": total_donations,
            "lives_helped": lives_helped,
            "last_donation": history.first(),
        }
    )


# =========================================================
# DONOR ALERTS
# =========================================================

def donor_alerts(request):

    if request.session.get("role") != "donor":

        return redirect("entry_page")

    donor = DonorProfile.objects.get(
        user_id=request.session["user_id"]
    )

    alerts = BloodRequest.objects.filter(
        status="Active",
        urgency__in=[
            "Emergency",
            "Urgent"
        ]
    ).order_by(
        "-created_at"
    )

    if donor.blood_group:

        alerts = alerts.filter(
            blood_group=donor.blood_group
        )

    responses = DonorResponse.objects.filter(
        donor=donor
    )

    responded_request_ids = responses.values_list(
        "blood_request_id",
        flat=True
    )

    return render(
        request,
        "donor/alerts.html",
        {
            "donor": donor,
            "alerts": alerts,
            "responded_request_ids":
                responded_request_ids,
        }
    )


# =========================================================
# NEEDER DASHBOARD
# =========================================================

def needer_dashboard(request):

    if request.session.get("role") != "needer":

        return redirect("entry_page")

    user_id = request.session.get(
        "user_id"
    )

    my_requests = BloodRequest.objects.filter(
        needer_id=user_id
    ).order_by(
        "-created_at"
    )

    active_requests = my_requests.filter(
        status="Active"
    ).count()

    fulfilled_requests = my_requests.filter(
        status="Fulfilled"
    ).count()

    response_count = DonorResponse.objects.filter(
        blood_request__needer_id=user_id
    ).count()

    active_request = my_requests.filter(
        status="Active"
    ).first()

    return render(
        request,
        "needer/needer_dahboard.html",
        {
            "name": request.session.get("name"),

            "username":
                request.session.get("username"),

            "role":
                request.session.get("role"),

            "active_count":
                active_requests,

            "fulfilled_count":
                fulfilled_requests,

            "response_count":
                response_count,

            "active_request":
                active_request,

        }
    )


# =========================================================
# CREATE BLOOD REQUEST
# =========================================================

def create_request(request):

    if request.session.get("role") != "needer":

        return redirect("entry_page")

    if request.method == "POST":

        patient_name = request.POST.get(
            "patientName",
            ""
        ).strip()

        patient_age = request.POST.get(
            "patientAge",
            ""
        )

        blood_group = request.POST.get(
            "bloodGroup",
            ""
        ).strip()

        units = request.POST.get(
            "units",
            ""
        )

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
            ""
        ).strip()

        additional_info = request.POST.get(
            "additionalInfo",
            ""
        ).strip()

        if not all([
            patient_name,
            patient_age,
            blood_group,
            units,
            hospital,
            location,
            urgency
        ]):

            messages.error(
                request,
                "Please fill all required fields."
            )

            return render(
                request,
                "needer/create_request.html"
            )

        BloodRequest.objects.create(

            needer_id=request.session["user_id"],

            patient_name=patient_name,

            patient_age=patient_age,

            blood_group=blood_group,

            units=units,

            received_units=0,

            hospital=hospital,

            location=location,

            urgency=urgency,

            additional_info=additional_info,

            status="Active",

            current_stage="Stage 1",

            progress=0

        )

        messages.success(
            request,
            "Blood request created successfully. Suitable donors can now be notified."
        )

        return redirect(
            "my_requests"
        )

    return render(
        request,
        "needer/create_request.html"
    )


# =========================================================
# MY REQUESTS
# =========================================================

def my_requests(request):

    if request.session.get("role") != "needer":

        return redirect("entry_page")

    requests_list = BloodRequest.objects.filter(
        needer_id=request.session["user_id"]
    ).order_by(
        "-created_at"
    )

    latest_request = requests_list.first()

    response_count = DonorResponse.objects.filter(
        blood_request__needer_id=
        request.session["user_id"]
    ).count()

    return render(
        request,
        "needer/my_requests.html",
        {
            "requests_list": requests_list,

            "latest_request": latest_request,

            "response_count":
                response_count,
        }
    )


# =========================================================
# CANCEL REQUEST
# =========================================================

def cancel_request(
    request,
    request_id
):

    if request.session.get("role") != "needer":

        return redirect("entry_page")

    blood_request = BloodRequest.objects.filter(
        id=request_id,
        needer_id=request.session["user_id"]
    ).first()

    if blood_request:

        blood_request.status = "Cancelled"

        blood_request.save()

        messages.success(
            request,
            "Your blood request has been cancelled."
        )

    return redirect(
        "my_requests"
    )


# =========================================================
# FIND DONOR
# =========================================================

def find_donor(request):

    if request.session.get("role") not in [
        "needer",
        "admin"
    ]:

        return redirect("entry_page")

    blood_group = request.GET.get(
        "blood_group",
        "all"
    )

    location = request.GET.get(
        "location",
        ""
    ).strip()

    distance = request.GET.get(
        "distance",
        "all"
    )

    donors = DonorProfile.objects.filter(
        is_available=True,
        user__is_blocked=False
    ).select_related(
        "user"
    )

    if blood_group != "all":

        donors = donors.filter(
            blood_group=blood_group
        )

    if location:

        donors = donors.filter(
            location__icontains=location
        )

    if distance != "all":

        try:

            distance_value = float(
                distance
            )

            donors = donors.filter(
                distance_km__lte=distance_value
            )

        except ValueError:

            pass

    return render(
        request,
        "needer/find_donor.html",
        {
            "donors": donors,

            "blood_group":
                blood_group,

            "location":
                location,

            "distance":
                distance
        }
    )


# =========================================================
# SOS TRACKING
# =========================================================

def sos_tracking(
    request,
    request_id
):

    if request.session.get("role") not in [
        "needer",
        "admin"
    ]:

        return redirect("entry_page")

    try:

        blood_request = BloodRequest.objects.select_related(
            "needer"
        ).get(
            id=request_id
        )

    except BloodRequest.DoesNotExist:

        messages.error(
            request,
            "SOS request not found."
        )

        return redirect(
            "my_requests"
        )

    # Needer can only see own request
    if request.session.get("role") == "needer":

        if blood_request.needer_id != request.session["user_id"]:

            messages.error(
                request,
                "You are not allowed to view this request."
            )

            return redirect(
                "my_requests"
            )

    responses = DonorResponse.objects.filter(
        blood_request=blood_request
    ).select_related(
        "donor__user"
    )

    response_count = responses.count()

    received_units = blood_request.received_units

    remaining_units = max(
        blood_request.units - received_units,
        0
    )

    progress = blood_request.progress

    return render(
        request,
        "needer/sos_tracking.html",
        {
            "blood_request":
                blood_request,

            "responses":
                responses,

            "response_count":
                response_count,

            "received_units":
                received_units,

            "remaining_units":
                remaining_units,

            "progress":
                progress,
        }
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def admin_dashboard(request):

    if request.session.get("role") != "admin":

        return redirect("entry_page")

    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    total_users = LoginUser.objects.count()

    total_donors = LoginUser.objects.filter(
        role="donor"
    ).count()

    total_needers = LoginUser.objects.filter(
        role="needer"
    ).count()

    pending_users = LoginUser.objects.filter(
        is_verified=False
    ).exclude(
        role="admin"
    ).count()

    blocked_users = LoginUser.objects.filter(
        is_blocked=True
    ).count()

    users = LoginUser.objects.all().order_by(
        "-created_at"
    )[:20]

    # -----------------------------------------------------
    # SOS
    # -----------------------------------------------------

    active_sos = BloodRequest.objects.filter(
        status="Active"
    )

    critical_sos = active_sos.filter(
        urgency="Emergency"
    ).count()

    high_sos = active_sos.filter(
        urgency="Urgent"
    ).count()

    normal_sos = active_sos.filter(
        urgency="Normal"
    ).count()

    total_sos = active_sos.count()

    # -----------------------------------------------------
    # ALL REQUESTS
    # -----------------------------------------------------

    total_requests = BloodRequest.objects.count()

    successful_matches = DonorResponse.objects.count()

    successful_donations = DonationHistory.objects.filter(
        status="Completed"
    ).count()

    failed_requests = BloodRequest.objects.filter(
        status="Cancelled"
    ).count()

    # -----------------------------------------------------
    # HOSPITALS
    # -----------------------------------------------------

    hospitals = Hospital.objects.all().order_by(
        "-created_at"
    )[:20]

    total_hospitals = Hospital.objects.count()

    verified_hospitals = Hospital.objects.filter(
        is_verified=True
    ).count()

    pending_hospitals = Hospital.objects.filter(
        is_verified=False,
        is_blocked=False
    ).count()

    # -----------------------------------------------------
    # SUSPICIOUS REQUESTS
    # -----------------------------------------------------

    five_minutes_ago = (
        timezone.now() -
        timedelta(minutes=5)
    )

    suspicious_requests = (
        BloodRequest.objects
        .filter(
            created_at__gte=five_minutes_ago
        )
        .values(
            "needer",
            "needer__name",
            "needer__username"
        )
        .annotate(
            request_count=Count("id")
        )
        .filter(
            request_count__gte=10
        )
    )

    # -----------------------------------------------------
    # RECENT REQUESTS
    # -----------------------------------------------------

    recent_requests = BloodRequest.objects.select_related(
        "needer"
    ).order_by(
        "-created_at"
    )[:20]

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = {

        "name":
            request.session.get("name"),

        "username":
            request.session.get("username"),

        "role":
            request.session.get("role"),

        # Users
        "total_users":
            total_users,

        "total_donors":
            total_donors,

        "total_needers":
            total_needers,

        "pending_users":
            pending_users,

        "blocked_users":
            blocked_users,

        "users":
            users,

        # SOS
        "critical_sos":
            critical_sos,

        "high_sos":
            high_sos,

        "normal_sos":
            normal_sos,

        "total_sos":
            total_sos,

        "active_sos":
            active_sos,

        # Analytics
        "total_requests":
            total_requests,

        "successful_matches":
            successful_matches,

        "failed_requests":
            failed_requests,

        "successful_donations":
            successful_donations,

        # Hospitals
        "hospitals":
            hospitals,

        "total_hospitals":
            total_hospitals,

        "verified_hospitals":
            verified_hospitals,

        "pending_hospitals":
            pending_hospitals,

        # Fraud
        "suspicious_requests":
            suspicious_requests,

        # Recent requests
        "recent_requests":
            recent_requests,
    }

    return render(
        request,
        "hemohub/admin_dashboard.html",
        context
    )


# =========================================================
# ADMIN VERIFY USER
# =========================================================

def admin_verify_user(
    request,
    user_id
):

    if request.session.get("role") != "admin":

        return redirect("entry_page")

    try:

        user = LoginUser.objects.get(
            id=user_id
        )

        user.is_verified = True

        user.is_blocked = False

        user.save()

        messages.success(
            request,
            f"{user.name} has been verified successfully."
        )

    except LoginUser.DoesNotExist:

        messages.error(
            request,
            "User not found."
        )

    return redirect(
        "admin_dashboard"
    )


# =========================================================
# ADMIN BLOCK USER
# =========================================================

def admin_block_user(
    request,
    user_id
):

    if request.session.get("role") != "admin":

        return redirect("entry_page")

    try:

        user = LoginUser.objects.get(
            id=user_id
        )

        if user.role == "admin":

            messages.error(
                request,
                "Admin accounts cannot be blocked."
            )

        else:

            user.is_blocked = True

            user.save()

            messages.success(
                request,
                f"{user.name} has been blocked."
            )

    except LoginUser.DoesNotExist:

        messages.error(
            request,
            "User not found."
        )

    return redirect(
        "admin_dashboard"
    )


# =========================================================
# ADMIN UNBLOCK USER
# =========================================================

def admin_unblock_user(
    request,
    user_id
):

    if request.session.get("role") != "admin":

        return redirect("entry_page")

    try:

        user = LoginUser.objects.get(
            id=user_id
        )

        user.is_blocked = False

        user.save()

        messages.success(
            request,
            f"{user.name} has been unblocked."
        )

    except LoginUser.DoesNotExist:

        messages.error(
            request,
            "User not found."
        )

    return redirect(
        "admin_dashboard"
    )


# =========================================================
# ADMIN VERIFY HOSPITAL
# =========================================================

def admin_verify_hospital(
    request,
    hospital_id
):

    if request.session.get("role") != "admin":

        return redirect("entry_page")

    try:

        hospital = Hospital.objects.get(
            id=hospital_id
        )

        hospital.is_verified = True

        hospital.is_blocked = False

        hospital.save()

        messages.success(
            request,
            f"{hospital.name} has been verified."
        )

    except Hospital.DoesNotExist:

        messages.error(
            request,
            "Hospital not found."
        )

    return redirect(
        "admin_dashboard"
    )


# =========================================================
# ADMIN REJECT / BLOCK HOSPITAL
# =========================================================

def admin_reject_hospital(
    request,
    hospital_id
):

    if request.session.get("role") != "admin":

        return redirect("entry_page")

    try:

        hospital = Hospital.objects.get(
            id=hospital_id
        )

        hospital.is_blocked = True

        hospital.is_verified = False

        hospital.save()

        messages.success(
            request,
            f"{hospital.name} has been rejected."
        )

    except Hospital.DoesNotExist:

        messages.error(
            request,
            "Hospital not found."
        )

    return redirect(
        "admin_dashboard"
    )


# =========================================================
# ADMIN UPDATE REQUEST STAGE
# =========================================================

def admin_update_sos_stage(
    request,
    request_id
):

    if request.session.get("role") != "admin":

        return redirect("entry_page")

    try:

        blood_request = BloodRequest.objects.get(
            id=request_id
        )

    except BloodRequest.DoesNotExist:

        messages.error(
            request,
            "SOS request not found."
        )

        return redirect(
            "admin_dashboard"
        )

    if request.method == "POST":

        stage = request.POST.get(
            "stage",
            ""
        )

        valid_stages = [
            "Stage 1",
            "Stage 2",
            "Stage 3",
            "Admin Escalation",
            "Completed"
        ]

        if stage in valid_stages:

            blood_request.current_stage = stage

            if stage == "Stage 1":

                blood_request.progress = 25

            elif stage == "Stage 2":

                blood_request.progress = 50

            elif stage == "Stage 3":

                blood_request.progress = 75

            elif stage == "Admin Escalation":

                blood_request.progress = 90

            elif stage == "Completed":

                blood_request.progress = 100
                blood_request.status = "Fulfilled"

            blood_request.save()

            messages.success(
                request,
                "SOS stage updated successfully."
            )

    return redirect(
        "admin_dashboard"
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_user(request):

    request.session.flush()

    return redirect(
        "entry_page"
    )
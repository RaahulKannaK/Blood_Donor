from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

from .models import (
    LoginUser,
    DonorProfile,
    BloodRequest,
    DonorResponse,
    DonationHistory
)


# =========================================================
# FIRST PAGE
# NAME + PASSWORD
# =========================================================

def entry_page(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        password = request.POST.get("password", "")

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

        if check_password(password, user.password):

            request.session["person_id"] = user.id
            request.session["person_name"] = user.name

            return redirect("login")

        else:

            messages.error(
                request,
                "Name or password is incorrect."
            )

    return render(
        request,
        "hemohub/entry.html"
    )


# =========================================================
# SECOND PAGE
# ROLE + USERNAME + PASSWORD
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

            # Make sure donor profile exists
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

        # -------------------------------------------------
        # CREATE LOGIN USER
        # -------------------------------------------------

        user = LoginUser.objects.create(
            name=name,
            age=age,
            username=username,
            password=make_password(password),
            role=role
        )

        # -------------------------------------------------
        # CREATE DONOR PROFILE
        # -------------------------------------------------

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

        return redirect(
            "entry_page"
        )

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

    # -----------------------------------------------------
    # BLOOD REQUESTS MATCHING DONOR BLOOD GROUP
    # -----------------------------------------------------

    nearby_requests = BloodRequest.objects.filter(
        status="Active",
        blood_group=donor.blood_group
    ).order_by(
        "-created_at"
    )

    nearby_count = nearby_requests.count()

    # -----------------------------------------------------
    # DONATION HISTORY
    # -----------------------------------------------------

    donation_history = DonationHistory.objects.filter(
        donor=donor
    ).order_by(
        "-donation_date"
    )

    total_donations = donation_history.count()

    # Simple calculation
    lives_helped = total_donations * 3

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

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

        return redirect(
            "entry_page"
        )

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

        # -------------------------------------------------
        # UPDATE LOGIN USER
        # -------------------------------------------------

        if name:
            donor.user.name = name

        if age:
            donor.user.age = age

        donor.user.save()

        # -------------------------------------------------
        # UPDATE DONOR PROFILE
        # -------------------------------------------------

        if blood_group:
            donor.blood_group = blood_group

        donor.phone = phone

        donor.location = location

        if last_donation:
            donor.last_donation_date = last_donation

        else:
            donor.last_donation_date = None

        donor.save()

        # Update session name
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

        "last_donation_date": donor.last_donation_date,

        "is_available": donor.is_available,

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

        return redirect(
            "entry_page"
        )

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

        if availability == "on":

            donor.is_available = True

        else:

            donor.is_available = False

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
# DONOR BLOOD RADAR
# =========================================================

def blood_radar(request):

    if request.session.get("role") != "donor":

        return redirect(
            "entry_page"
        )

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

    # -----------------------------------------------------
    # BLOOD GROUP FILTER
    # -----------------------------------------------------

    if blood_group != "all":

        requests_list = requests_list.filter(
            blood_group=blood_group
        )

    # -----------------------------------------------------
    # DONOR BLOOD GROUP
    # -----------------------------------------------------

    if blood_group == "all" and donor.blood_group:

        requests_list = requests_list.filter(
            blood_group=donor.blood_group
        )

    context = {

        "donor": donor,

        "requests_list": requests_list,

        "blood_group": blood_group,

        "radius": radius,

    }

    return render(
        request,
        "donor/radar.html",
        context
    )


# =========================================================
# DONOR REQUESTS
# =========================================================

def donor_requests(request):

    if request.session.get("role") != "donor":

        return redirect(
            "entry_page"
        )

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

    status_filter = request.GET.get(
        "status",
        "all"
    )

    requests_list = BloodRequest.objects.filter(
        status="Active"
    ).order_by(
        "-created_at"
    )

    # Show donor's blood group by default
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

    # -----------------------------------------------------
    # DONOR'S EXISTING RESPONSES
    # -----------------------------------------------------

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

        "responded_request_ids": responded_request_ids,

    }

    return render(
        request,
        "donor/requests.html",
        context
    )


# =========================================================
# RESPOND TO BLOOD REQUEST
# =========================================================

def respond_to_request(request, request_id):

    if request.session.get("role") != "donor":

        return redirect(
            "entry_page"
        )

    user_id = request.session.get(
        "user_id"
    )

    try:

        donor = DonorProfile.objects.get(
            user_id=user_id
        )

    except DonorProfile.DoesNotExist:

        messages.error(
            request,
            "Donor profile not found."
        )

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

    # -----------------------------------------------------
    # CHECK AVAILABILITY
    # -----------------------------------------------------

    if not donor.is_available:

        messages.error(
            request,
            "You are currently unavailable for donation."
        )

        return redirect(
            "donor_requests"
        )

    # -----------------------------------------------------
    # CHECK BLOOD GROUP
    # -----------------------------------------------------

    if donor.blood_group != blood_request.blood_group:

        messages.error(
            request,
            "Your blood group does not match this request."
        )

        return redirect(
            "donor_requests"
        )

    # -----------------------------------------------------
    # CHECK DUPLICATE RESPONSE
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CREATE RESPONSE
    # -----------------------------------------------------

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

        return redirect(
            "entry_page"
        )

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

    history = DonationHistory.objects.filter(
        donor=donor
    ).order_by(
        "-donation_date"
    )

    total_donations = history.count()

    lives_helped = total_donations * 3

    context = {

        "donor": donor,

        "history": history,

        "total_donations": total_donations,

        "lives_helped": lives_helped,

        "last_donation": history.first(),

    }

    return render(
        request,
        "donor/history.html",
        context
    )


# =========================================================
# DONOR ALERTS
# =========================================================

def donor_alerts(request):

    if request.session.get("role") != "donor":

        return redirect(
            "entry_page"
        )

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

    alerts = BloodRequest.objects.filter(
        status="Active",
        urgency__in=[
            "Emergency",
            "Urgent"
        ]
    ).order_by(
        "-created_at"
    )

    # Match donor blood group
    if donor.blood_group:

        alerts = alerts.filter(
            blood_group=donor.blood_group
        )

    # Existing responses
    responses = DonorResponse.objects.filter(
        donor=donor
    )

    responded_request_ids = responses.values_list(
        "blood_request_id",
        flat=True
    )

    context = {

        "donor": donor,

        "alerts": alerts,

        "responded_request_ids": responded_request_ids,

    }

    return render(
        request,
        "donor/alerts.html",
        context
    )


# =========================================================
# NEEDER DASHBOARD
# =========================================================

def needer_dashboard(request):

    if request.session.get("role") != "needer":

        return redirect(
            "entry_page"
        )

    my_requests = BloodRequest.objects.filter(
        needer_id=request.session["user_id"]
    ).order_by(
        "-created_at"
    )

    active_requests = my_requests.filter(
        status="Active"
    ).count()

    # Count donor responses to needer's requests
    response_count = DonorResponse.objects.filter(
        blood_request__needer_id=request.session["user_id"]
    ).count()

    context = {

        "name": request.session.get("name"),

        "username": request.session.get("username"),

        "role": request.session.get("role"),

        "active_count": active_requests,

        "fulfilled_count": my_requests.filter(
            status="Fulfilled"
        ).count(),

        "response_count": response_count,

        "active_request": my_requests.filter(
            status="Active"
        ).first(),

    }

    return render(
        request,
        "needer/needer_dahboard.html",
        context
    )


# =========================================================
# CREATE BLOOD REQUEST
# =========================================================

def create_request(request):

    if request.session.get("role") != "needer":

        return redirect(
            "entry_page"
        )

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

            hospital=hospital,

            location=location,

            urgency=urgency,

            additional_info=additional_info

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

        return redirect(
            "entry_page"
        )

    requests_list = BloodRequest.objects.filter(
        needer_id=request.session["user_id"]
    ).order_by(
        "-created_at"
    )

    latest_request = requests_list.first()

    # Actual donor responses
    response_count = DonorResponse.objects.filter(
        blood_request__needer_id=request.session["user_id"]
    ).count()

    context = {

        "requests_list": requests_list,

        "latest_request": latest_request,

        "response_count": response_count,

    }

    return render(
        request,
        "needer/my_requests.html",
        context
    )


# =========================================================
# CANCEL REQUEST
# =========================================================

def cancel_request(request, request_id):

    if request.session.get("role") != "needer":

        return redirect(
            "entry_page"
        )

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

        return redirect(
            "entry_page"
        )

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
        is_available=True
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
            "blood_group": blood_group,
            "location": location,
            "distance": distance
        }
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def admin_dashboard(request):

    if request.session.get("role") != "admin":

        return redirect(
            "entry_page"
        )

    context = {

        "name": request.session.get(
            "name"
        ),

        "username": request.session.get(
            "username"
        ),

        "role": request.session.get(
            "role"
        ),

    }

    return render(
        request,
        "hemohub/admin_dashboard.html",
        context
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_user(request):

    request.session.flush()

    return redirect(
        "entry_page"
    )
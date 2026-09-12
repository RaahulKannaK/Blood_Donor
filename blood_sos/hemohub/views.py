from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from .models import LoginUser,DonorProfile,BloodRequest


# ---------------------------------------------------------
# FIRST PAGE
# NAME + PASSWORD
# ---------------------------------------------------------

def entry_page(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        password = request.POST.get("password", "")

        print("================================")
        print("ENTRY LOGIN DEBUG")
        print("Entered name:", name)
        print("Password entered:", password)

        if not name or not password:
            messages.error(
                request,
                "Please enter your name and password."
            )
            return render(request, "hemohub/entry.html")

        try:
            user = LoginUser.objects.get(name__iexact=name)

            print("User found:", user.name)
            print("Username:", user.username)
            print("Role:", user.role)
            print("Stored password:", user.password)

        except LoginUser.DoesNotExist:

            print("USER NOT FOUND")

            messages.error(
                request,
                "Name or password is incorrect."
            )

            return render(request, "hemohub/entry.html")

        password_valid = check_password(
            password,
            user.password
        )

        print("Password valid:", password_valid)

        if password_valid:

            print("LOGIN SUCCESS")

            request.session["person_id"] = user.id
            request.session["person_name"] = user.name

            return redirect("login")

        else:

            print("PASSWORD INCORRECT")

            messages.error(
                request,
                "Name or password is incorrect."
            )

    return render(request, "hemohub/entry.html")

# ---------------------------------------------------------
# SECOND PAGE
# ROLE + USERNAME + PASSWORD
# ---------------------------------------------------------

def login(request):

    # First page must be completed
    if "person_id" not in request.session:
        return redirect("entry_page")

    person_name = request.session.get("person_name")

    if request.method == "POST":

        role = request.POST.get("role", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not role:
            messages.error(request, "Please select a role.")
            return render(
                request,
                "hemohub/login.html",
                {"person_name": person_name}
            )

        if not username or not password:
            messages.error(request, "Please enter username and password.")
            return render(
                request,
                "hemohub/login.html",
                {"person_name": person_name}
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
                {"person_name": person_name}
            )

        # Verify password
        if not check_password(password, user.password):
            messages.error(
                request,
                "Invalid username, password or role."
            )

            return render(
                request,
                "hemohub/login.html",
                {"person_name": person_name}
            )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        request.session["user_id"] = user.id
        request.session["username"] = user.username
        request.session["role"] = user.role
        request.session["name"] = user.name

        # Remove temporary first-page session values
        request.session.pop("person_id", None)
        request.session.pop("person_name", None)

        # Redirect according to role
        if user.role == "admin":
            return redirect("admin_dashboard")

        elif user.role == "donor":
            return redirect("donor_dashboard")

        elif user.role == "needer":
            return redirect("needer_dashboard")

    return render(
        request,
        "hemohub/login.html",
        {"person_name": person_name}
    )


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

def register(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        age = request.POST.get("age", "")
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        role = request.POST.get("role", "").strip()

        # Required fields
        if not all([
            name,
            age,
            username,
            password,
            confirm_password,
            role
        ]):
            messages.error(request, "Please fill all fields.")
            return render(request, "hemohub/register.html")

        # Password confirmation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "hemohub/register.html")

        # Username already exists
        if LoginUser.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "hemohub/register.html")

        # Create user
        user = LoginUser.objects.create(
            name=name,
            age=age,
            username=username,
            password=make_password(password),
            role=role
        )

        messages.success(
            request,
            "Registration successful. Please login."
        )

        return redirect("entry_page")

    return render(request, "hemohub/register.html")


# ---------------------------------------------------------
# FORGOT PASSWORD
# ---------------------------------------------------------

def forgot_password(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()

        if not username:
            messages.error(request, "Please enter your username.")
            return render(request, "hemohub/forgot_password.html")

        try:
            user = LoginUser.objects.get(
                username__iexact=username
            )
        except LoginUser.DoesNotExist:
            messages.error(request, "Username not found.")
            return render(request, "hemohub/forgot_password.html")

        # For now, redirect to reset page
        request.session["reset_user_id"] = user.id

        return redirect("reset_password")

    return render(request, "hemohub/forgot_password.html")


# ---------------------------------------------------------
# RESET PASSWORD
# ---------------------------------------------------------

def reset_password(request):

    user_id = request.session.get("reset_user_id")

    if not user_id:
        return redirect("forgot_password")

    try:
        user = LoginUser.objects.get(id=user_id)
    except LoginUser.DoesNotExist:
        return redirect("forgot_password")

    if request.method == "POST":

        new_password = request.POST.get("password", "")
        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        if not new_password or not confirm_password:
            messages.error(request, "Please enter both passwords.")
            return render(
                request,
                "hemohub/reset_password.html"
            )

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(
                request,
                "hemohub/reset_password.html"
            )

        user.password = make_password(new_password)
        user.save()

        request.session.pop("reset_user_id", None)

        messages.success(
            request,
            "Password changed successfully."
        )

        return redirect("entry_page")

    return render(
        request,
        "hemohub/reset_password.html"
    )


# ---------------------------------------------------------
# DONOR DASHBOARD
# ---------------------------------------------------------

def donor_dashboard(request):

    if request.session.get("role") != "donor":
        return redirect("entry_page")

    context = {
        "name": request.session.get("name"),
        "username": request.session.get("username"),
        "role": request.session.get("role"),
    }

    return render(
        request,
        "hemohub/donor_dashboard.html",
        context
    )


# ---------------------------------------------------------
# NEEDER DASHBOARD
# ---------------------------------------------------------

def needer_dashboard(request):

    if request.session.get("role") != "needer":
        return redirect("entry_page")

    my_requests = BloodRequest.objects.filter(
        needer_id=request.session["user_id"]
    ).order_by("-created_at")

    active_requests = my_requests.filter(status="Active").count()

    context = {
        "name": request.session.get("name"),
        "username": request.session.get("username"),
        "role": request.session.get("role"),
        "active_count": active_requests,
        "fulfilled_count": my_requests.filter(status="Fulfilled").count(),
        "response_count": 0,  # update when you add a DonorResponse model
        "active_request": my_requests.filter(status="Active").first(),
    }

    return render(request, "needer/needer_dahboard.html", context)


# ---------------------------------------------------------
# CREATE BLOOD REQUEST
# ---------------------------------------------------------

def create_request(request):

    if request.session.get("role") != "needer":
        return redirect("entry_page")

    if request.method == "POST":

        patient_name = request.POST.get("patientName", "").strip()
        patient_age = request.POST.get("patientAge", "")
        blood_group = request.POST.get("bloodGroup", "").strip()
        units = request.POST.get("units", "")
        hospital = request.POST.get("hospital", "").strip()
        location = request.POST.get("location", "").strip()
        urgency = request.POST.get("urgency", "").strip()
        additional_info = request.POST.get("additionalInfo", "").strip()

        # Validation
        if not all([
            patient_name, patient_age, blood_group,
            units, hospital, location, urgency
        ]):
            messages.error(request, "Please fill all required fields.")
            return render(request, "needer/create_request.html")

        BloodRequest.objects.create(
            needer_id=request.session["user_id"],
            patient_name=patient_name,
            patient_age=patient_age,
            blood_group=blood_group,
            units=units,
            hospital=hospital,
            location=location,
            urgency=urgency,
            additional_info=additional_info,
        )

        messages.success(
            request,
            "Blood request created successfully. "
            "Suitable donors can now be notified."
        )

        return redirect("my_requests")

    return render(request, "needer/create_request.html")


# ---------------------------------------------------------
# MY REQUESTS
# ---------------------------------------------------------

def my_requests(request):

    if request.session.get("role") != "needer":
        return redirect("entry_page")

    requests_list = BloodRequest.objects.filter(
        needer_id=request.session["user_id"]
    ).order_by("-created_at")

    return render(
        request,
        "needer/my_requests.html",
        {"requests_list": requests_list}
    )


# ---------------------------------------------------------
# CANCEL REQUEST
# ---------------------------------------------------------

def cancel_request(request, request_id):

    if request.session.get("role") != "needer":
        return redirect("entry_page")

    blood_request = BloodRequest.objects.filter(
        id=request_id,
        needer_id=request.session["user_id"]
    ).first()

    if blood_request:
        blood_request.status = "Cancelled"
        blood_request.save()
        messages.success(request, "Your blood request has been cancelled.")

    return redirect("my_requests")


# ---------------------------------------------------------
# FIND DONOR
# ---------------------------------------------------------

def find_donor(request):

    if request.session.get("role") not in ["needer", "admin"]:
        return redirect("entry_page")

    blood_group = request.GET.get("blood_group", "all")
    location = request.GET.get("location", "").strip()
    distance = request.GET.get("distance", "all")

    donors = DonorProfile.objects.filter(is_available=True).select_related("user")

    if blood_group != "all":
        donors = donors.filter(blood_group=blood_group)

    if location:
        donors = donors.filter(location__icontains=location)

    if distance != "all":
        donors = donors.filter(distance_km__lte=float(distance))

    return render(
        request,
        "needer/find_donor.html",
        {"donors": donors}
    )

# ---------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------

def admin_dashboard(request):

    if request.session.get("role") != "admin":
        return redirect("entry_page")

    context = {
        "name": request.session.get("name"),
        "username": request.session.get("username"),
        "role": request.session.get("role"),
    }

    return render(
        request,
        "hemohub/admin_dashboard.html",
        context
    )


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

def logout_user(request):

    request.session.flush()

    return redirect("entry_page")
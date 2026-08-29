from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from .models import LoginUser


# ---------------------------------------------------------
# FIRST PAGE
# NAME + PASSWORD
# ---------------------------------------------------------

def entry_page(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        password = request.POST.get("password", "")

        if not name or not password:
            messages.error(request, "Please enter your name and password.")
            return render(request, "hemohub/entry.html")

        try:
            user = LoginUser.objects.get(name__iexact=name)
        except LoginUser.DoesNotExist:
            messages.error(request, "Name or password is incorrect.")
            return render(request, "hemohub/entry.html")

        # Check hashed password
        if check_password(password, user.password):

            # Store person information temporarily
            request.session["person_id"] = user.id
            request.session["person_name"] = user.name

            return redirect("login")

        else:
            messages.error(request, "Name or password is incorrect.")

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

    context = {
        "name": request.session.get("name"),
        "username": request.session.get("username"),
        "role": request.session.get("role"),
    }

    return render(
        request,
        "hemohub/needer_dashboard.html",
        context
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
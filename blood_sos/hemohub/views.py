from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import json
from django.contrib.auth.hashers import check_password, make_password
from math import radians, sin, cos, sqrt, atan2

from .models import (
    LoginUser,
    DonorProfile,
    BloodRequest,
    DonorResponse,
    DonationHistory
)

try:
    from .services.distance import validate_coordinates
    from .services.routing import get_road_distance_and_eta
except ImportError:

    def validate_coordinates(latitude, longitude):
        try:
            return (
                -90 <= float(latitude) <= 90
                and -180 <= float(longitude) <= 180
            )
        except (TypeError, ValueError):
            return False

    def get_road_distance_and_eta(*args, **kwargs):
        return None


MAX_MATCH_DISTANCE_KM = 15.0


def entry_page(request):
    return render(request, "hemohub/entry.html")


def login(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        password = request.POST.get("password", "").strip()

        if not name:
            messages.error(request, "Please enter your name.")
            return render(request, "hemohub/entry.html")

        if not password:
            messages.error(request, "Please enter your password.")
            return render(request, "hemohub/entry.html")

        try:
            user = LoginUser.objects.get(name=name)

        except LoginUser.DoesNotExist:
            messages.error(request, "Invalid name or password.")
            return render(request, "hemohub/entry.html")

        except LoginUser.MultipleObjectsReturned:
            messages.error(
                request,
                "Multiple accounts found with this name. "
                "Please use a unique name."
            )
            return render(request, "hemohub/entry.html")

        if user.is_blocked:
            messages.error(
                request,
                "Your account has been blocked by the administrator."
            )
            return render(request, "hemohub/entry.html")

        password_valid = check_password(
            password,
            user.password
        )

        if not password_valid:
            messages.error(request, "Invalid name or password.")
            return render(request, "hemohub/entry.html")

        request.session["user_id"] = user.id
        request.session["username"] = user.username
        request.session["name"] = user.name
        request.session["role"] = user.role

        if user.role == "donor":
            return redirect("donor_dashboard")

        elif user.role == "needer":
            return redirect("needer_dashboard")

        elif user.role == "admin":
            return redirect("admin_dashboard")

        messages.error(request, "Invalid account role.")
        return render(request, "hemohub/entry.html")

    return render(request, "hemohub/entry.html")


def register(request):

    if request.method == "POST":

        # =====================================================
        # GET FORM DATA
        # =====================================================

        name = request.POST.get("name", "").strip()
        username = request.POST.get("username", "").strip()
        age = request.POST.get("age", "").strip()
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get(
            "confirm_password",
            ""
        ).strip()
        role = request.POST.get("role", "").strip()


        # =====================================================
        # REQUIRED FIELD VALIDATION
        # =====================================================

        if not all([
            name,
            username,
            age,
            password,
            confirm_password,
            role
        ]):

            messages.error(
                request,
                "Please fill all required fields."
            )

            return redirect("register")


        # =====================================================
        # PASSWORD CONFIRMATION
        # =====================================================

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("register")


        # =====================================================
        # USERNAME CHECK
        # =====================================================

        if LoginUser.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("register")


        # =====================================================
        # NAME CHECK
        # =====================================================

        if LoginUser.objects.filter(
            name=name
        ).exists():

            messages.error(
                request,
                "An account with this name already exists."
            )

            return redirect("register")


        # =====================================================
        # AGE VALIDATION
        # =====================================================

        try:

            age = int(age)

        except ValueError:

            messages.error(
                request,
                "Please enter a valid age."
            )

            return redirect("register")


        if age < 1 or age > 120:

            messages.error(
                request,
                "Please enter a valid age between 1 and 120."
            )

            return redirect("register")


        # =====================================================
        # ROLE VALIDATION
        # =====================================================

        allowed_roles = [
            "donor",
            "needer",
            "admin"
        ]

        if role not in allowed_roles:

            messages.error(
                request,
                "Please select a valid role."
            )

            return redirect("register")


        # =====================================================
        # CREATE LOGIN USER
        # =====================================================

        LoginUser.objects.create(

            name=name,

            age=age,

            username=username,

            password=make_password(password),

            role=role

        )


        # =====================================================
        # SUCCESS MESSAGE
        # =====================================================

        messages.success(
            request,
            "Registration successful. Please login."
        )

        return redirect("login")


    # =========================================================
    # GET REQUEST
    # =========================================================

    return render(
        request,
        "hemohub/register.html"
    )

def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        try:
            user = LoginUser.objects.get(
                username=username,
                email=email
            )

            request.session["reset_user_id"] = user.id

            return redirect("reset_password")

        except LoginUser.DoesNotExist:
            messages.error(
                request,
                "Username and email do not match."
            )

    return render(
        request,
        "forgot_password.html"
    )


def reset_password(request):
    if "reset_user_id" not in request.session:
        return redirect("forgot_password")

    if request.method == "POST":
        password = request.POST.get(
            "password",
            ""
        ).strip()

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        ).strip()

        if not password or not confirm_password:
            messages.error(
                request,
                "Please enter both password fields."
            )
            return redirect("reset_password")

        if password != confirm_password:
            messages.error(
                request,
                "Passwords do not match."
            )
            return redirect("reset_password")

        user_id = request.session.get(
            "reset_user_id"
        )

        try:
            user = LoginUser.objects.get(
                id=user_id
            )

            user.password = make_password(password)
            user.save()

            del request.session["reset_user_id"]

            messages.success(
                request,
                "Password reset successfully."
            )

            return redirect("login")

        except LoginUser.DoesNotExist:
            return redirect("forgot_password")

    return render(
        request,
        "reset_password.html"
    )


def donor_dashboard(request):
    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get("user_id")

    try:
        user = LoginUser.objects.get(
            id=user_id,
            role="donor"
        )

    except LoginUser.DoesNotExist:
        return redirect("login")

    try:
        donor = DonorProfile.objects.get(
            user=user
        )

    except DonorProfile.DoesNotExist:
        donor = None

    response_count = (
        DonorResponse.objects
        .filter(donor=donor)
        .count()
        if donor
        else 0
    )

    donation_count = (
        DonationHistory.objects
        .filter(donor=donor)
        .count()
        if donor
        else 0
    )

    context = {
        "name": user.name,
        "username": user.username,
        "age": user.age,
        "role": user.role,
        "donor": donor,
        "response_count": response_count,
        "donation_count": donation_count
    }

    return render(
        request,
        "donor/dashboard.html",
        context
    )


def donor_profile(request):
    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get("user_id")

    try:
        user = LoginUser.objects.get(
            id=user_id,
            role="donor"
        )

    except LoginUser.DoesNotExist:
        return redirect("login")

    donor, created = DonorProfile.objects.get_or_create(
        user=user
    )

    if request.method == "POST":

        name = request.POST.get(
            "name",
            user.name or ""
        ).strip()

        age = request.POST.get(
            "age",
            user.age or ""
        ).strip()

        blood_group = request.POST.get(
            "blood",
            donor.blood_group or ""
        ).strip()

        phone = request.POST.get(
            "phone",
            donor.phone or ""
        ).strip()

        last_donation = request.POST.get(
            "lastDonation",
            ""
        ).strip()

        location = request.POST.get(
            "location",
            donor.location or ""
        ).strip()

        latitude = request.POST.get(
            "latitude",
            ""
        ).strip()

        longitude = request.POST.get(
            "longitude",
            ""
        ).strip()

        user.name = name
        user.age = age
        user.save()

        donor.blood_group = blood_group
        donor.phone = phone
        donor.location = location

        if last_donation:
            try:
                from datetime import datetime

                donor.last_donation_date = datetime.strptime(
                    last_donation,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                donor.last_donation_date = None

        else:
            donor.last_donation_date = None

        if latitude:
            try:
                latitude_value = float(latitude)

                if -90 <= latitude_value <= 90:
                    donor.latitude = latitude_value

            except (ValueError, TypeError):
                pass

        if longitude:
            try:
                longitude_value = float(longitude)

                if -180 <= longitude_value <= 180:
                    donor.longitude = longitude_value

            except (ValueError, TypeError):
                pass

        donor.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("donor_profile")

    last_donation = ""

    if donor.last_donation_date:
        last_donation = donor.last_donation_date.strftime(
            "%Y-%m-%d"
        )

    saved_latitude = ""
    saved_longitude = ""

    if donor.latitude is not None:
        saved_latitude = donor.latitude

    if donor.longitude is not None:
        saved_longitude = donor.longitude

    context = {
        "user": user,
        "name": user.name or "",
        "username": user.username or "",
        "age": user.age or "",
        "donor": donor,
        "blood": donor.blood_group or "",
        "blood_group": donor.blood_group or "",
        "phone": donor.phone or "",
        "lastDonation": last_donation,
        "location": donor.location or "",
        "latitude": saved_latitude,
        "longitude": saved_longitude,
        "accuracy": ""
    }

    return render(
        request,
        "donor/profile.html",
        context
    )


def update_availability(request):
    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get("user_id")

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
        return redirect("login")

    if request.method == "POST":
        availability = request.POST.get(
            "availability"
        )

        donor.is_available = (
            str(availability)
            .strip()
            .lower()
            in [
                "true",
                "1",
                "yes",
                "on",
                "available"
            ]
        )

        donor.save(
            update_fields=["is_available"]
        )

        messages.success(
            request,
            "Availability updated successfully."
        )

    return redirect(
        "donor_dashboard"
    )


def save_location(request):
    if "user_id" not in request.session:
        return JsonResponse(
            {
                "success": False,
                "message": "Please login first."
            },
            status=401
        )

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "POST request required."
            },
            status=405
        )

    try:
        user = LoginUser.objects.get(
            id=request.session.get("user_id")
        )

    except LoginUser.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "message": "User not found."
            },
            status=401
        )

    latitude = request.POST.get(
        "latitude"
    )

    longitude = request.POST.get(
        "longitude"
    )

    if not latitude or not longitude:
        try:
            data = json.loads(
                request.body.decode("utf-8")
            )

            latitude = data.get(
                "latitude"
            )

            longitude = data.get(
                "longitude"
            )

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
            AttributeError
        ):
            pass

    if not latitude or not longitude:
        return JsonResponse(
            {
                "success": False,
                "message": "Location data missing."
            },
            status=400
        )

    try:
        latitude = float(latitude)
        longitude = float(longitude)

    except (ValueError, TypeError):
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid location data."
            },
            status=400
        )

    if not validate_coordinates(
        latitude,
        longitude
    ):
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid GPS coordinates."
            },
            status=400
        )

    if user.role == "donor":

        try:
            donor = DonorProfile.objects.get(
                user=user
            )

        except DonorProfile.DoesNotExist:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Donor profile not found."
                },
                status=404
            )

        donor.latitude = latitude
        donor.longitude = longitude

        donor.save(
            update_fields=[
                "latitude",
                "longitude"
            ]
        )

    elif user.role == "needer":

        active_request = (
            BloodRequest.objects
            .filter(
                needer=user,
                status__iexact="Active"
            )
            .order_by("-created_at")
            .first()
        )

        if not active_request:
            return JsonResponse(
                {
                    "success": False,
                    "message": "No active blood request found."
                },
                status=404
            )

        active_request.latitude = latitude
        active_request.longitude = longitude

        active_request.save(
            update_fields=[
                "latitude",
                "longitude"
            ]
        )

    else:
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Location saving is not available "
                    "for this account."
                )
            },
            status=403
        )

    return JsonResponse(
        {
            "success": True,
            "message": "Location saved successfully.",
            "latitude": latitude,
            "longitude": longitude
        }
    )


def get_request_route(request, request_id):
    if "user_id" not in request.session:
        return JsonResponse(
            {
                "success": False,
                "message": "Please login first."
            },
            status=401
        )

    try:
        user = LoginUser.objects.get(
            id=request.session.get("user_id"),
            role="donor"
        )

        donor = DonorProfile.objects.get(
            user=user
        )

    except (
        LoginUser.DoesNotExist,
        DonorProfile.DoesNotExist
    ):
        return JsonResponse(
            {
                "success": False,
                "message": "Donor not found."
            },
            status=401
        )

    try:
        blood_request = BloodRequest.objects.get(
            id=request_id,
            status__iexact="Active"
        )

    except BloodRequest.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Blood request not found or "
                    "is no longer active."
                )
            },
            status=404
        )

    if (
        donor.latitude is None
        or donor.longitude is None
    ):
        return JsonResponse(
            {
                "success": False,
                "message": "Donor location is unavailable."
            },
            status=400
        )

    if (
        blood_request.latitude is None
        or blood_request.longitude is None
    ):
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Blood request location "
                    "is unavailable."
                )
            },
            status=400
        )

    try:
        donor_latitude = float(
            donor.latitude
        )

        donor_longitude = float(
            donor.longitude
        )

        request_latitude = float(
            blood_request.latitude
        )

        request_longitude = float(
            blood_request.longitude
        )

    except (ValueError, TypeError):
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid location coordinates."
            },
            status=400
        )

    if not validate_coordinates(
        donor_latitude,
        donor_longitude
    ):
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid donor coordinates."
            },
            status=400
        )

    if not validate_coordinates(
        request_latitude,
        request_longitude
    ):
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Invalid blood request coordinates."
                )
            },
            status=400
        )

    route_data = get_road_distance_and_eta(
        donor_latitude,
        donor_longitude,
        request_latitude,
        request_longitude
    )

    if not route_data:
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Road route could not be calculated."
                )
            },
            status=503
        )

    return JsonResponse(
        {
            "success": True,
            "request_id": blood_request.id,
            "start": {
                "latitude": donor_latitude,
                "longitude": donor_longitude
            },
            "destination": {
                "latitude": request_latitude,
                "longitude": request_longitude
            },
            "road_distance_km": route_data.get(
                "road_distance_km"
            ),
            "car_distance_km": route_data.get(
                "car_distance_km"
            ),
            "car_eta_minutes": route_data.get(
                "car_eta_minutes"
            ),
            "bike_distance_km": route_data.get(
                "bike_distance_km"
            ),
            "bike_eta_minutes": route_data.get(
                "bike_eta_minutes"
            ),
            "bus_distance_km": route_data.get(
                "bus_distance_km"
            ),
            "bus_eta_minutes": route_data.get(
                "bus_eta_minutes"
            ),
            "bus_waiting_minutes": route_data.get(
                "bus_waiting_minutes"
            ),
            "distance_type": route_data.get(
                "distance_type"
            ),
            "geometry": route_data.get(
                "geometry"
            ),
            "steps": route_data.get(
                "steps",
                []
            )
        }
    )


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

    except (ValueError, TypeError):
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
        return redirect("login")

    blood_requests = (
        BloodRequest.objects
        .filter(status__iexact="Active")
        .exclude(needer=user)
        .order_by("-created_at")
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
        "blood_requests": blood_requests
    }

    return render(
        request,
        "donor/requests.html",
        context
    )


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
        return redirect("login")

    donor_blood_group = (
        donor.blood_group or ""
    ).strip().upper()

    context = {
        "name": user.name,
        "username": user.username,
        "age": user.age,
        "donor": donor,
        "donor_blood_group": donor_blood_group,
        "requests_list": [],
        "responded_request_ids": set(),
        "status_filter": "all",
        "location_missing": False
    }

    if (
        donor.latitude is None
        or donor.longitude is None
    ):
        messages.warning(
            request,
            (
                "Please update your current location "
                "in your donor profile to see nearby "
                "blood requests."
            )
        )

        context["location_missing"] = True

        return render(
            request,
            "donor/requests.html",
            context
        )

    try:
        donor_latitude = float(
            donor.latitude
        )

        donor_longitude = float(
            donor.longitude
        )

    except (ValueError, TypeError):
        messages.warning(
            request,
            (
                "Your saved donor GPS coordinates are "
                "invalid. Please update your profile location."
            )
        )

        context["location_missing"] = True

        return render(
            request,
            "donor/requests.html",
            context
        )

    if not validate_coordinates(
        donor_latitude,
        donor_longitude
    ):
        messages.warning(
            request,
            (
                "Your saved donor GPS coordinates are "
                "invalid. Please update your profile location."
            )
        )

        context["location_missing"] = True

        return render(
            request,
            "donor/requests.html",
            context
        )

    status_filter = (
        request.GET.get(
            "status",
            "all"
        )
        .strip()
        .lower()
    )

    blood_requests = (
        BloodRequest.objects
        .filter(
            status__iexact="Active",
            blood_group__iexact=donor_blood_group
        )
        .exclude(needer=user)
        .order_by("-created_at")
    )

    if status_filter == "critical":
        blood_requests = blood_requests.filter(
            urgency__iexact="Emergency"
        )

    elif status_filter == "urgent":
        blood_requests = blood_requests.filter(
            urgency__iexact="Urgent"
        )

    elif status_filter == "normal":
        blood_requests = blood_requests.filter(
            urgency__iexact="Normal"
        )

    else:
        status_filter = "all"

    nearby_requests = []

    for blood_request in blood_requests:

        if (
            blood_request.latitude is None
            or blood_request.longitude is None
        ):
            continue

        try:
            request_latitude = float(
                blood_request.latitude
            )

            request_longitude = float(
                blood_request.longitude
            )

        except (ValueError, TypeError):
            continue

        if not validate_coordinates(
            request_latitude,
            request_longitude
        ):
            continue

        straight_distance = calculate_distance_km(
            donor_latitude,
            donor_longitude,
            request_latitude,
            request_longitude
        )

        if straight_distance is None:
            continue

        route_data = get_road_distance_and_eta(
            donor_latitude,
            donor_longitude,
            request_latitude,
            request_longitude
        )

        if not route_data:
            continue

        road_distance = route_data.get(
            "road_distance_km"
        )

        if road_distance is None:
            continue

        try:
            road_distance = float(
                road_distance
            )

        except (ValueError, TypeError):
            continue

        if road_distance > MAX_MATCH_DISTANCE_KM:
            continue

        if road_distance <= 5:
            matching_stage = "Stage 1: 0–5 km"

        elif road_distance <= 10:
            matching_stage = "Stage 2: 5–10 km"

        else:
            matching_stage = "Stage 3: 10–15 km"

        urgency = (
            blood_request.urgency or "Normal"
        ).strip().lower()

        urgency_priority = {
            "emergency": 1,
            "urgent": 2,
            "normal": 3
        }.get(
            urgency,
            3
        )

        existing_response = (
            DonorResponse.objects
            .filter(
                donor=donor,
                blood_request=blood_request
            )
            .order_by("-created_at")
            .first()
        )

        already_responded = (
            existing_response is not None
        )

        response_status = (
            existing_response.status
            if existing_response
            else None
        )

        item = {
            "id": blood_request.id,
            "blood_group": blood_request.blood_group,
            "location": blood_request.location,
            "urgency": blood_request.urgency,
            "distance_km": round(
                road_distance,
                2
            ),
            "straight_distance_km": round(
                straight_distance,
                2
            ),
            "car_distance_km": route_data.get(
                "car_distance_km",
                road_distance
            ),
            "car_eta_minutes": route_data.get(
                "car_eta_minutes"
            ),
            "bike_distance_km": route_data.get(
                "bike_distance_km"
            ),
            "bike_eta_minutes": route_data.get(
                "bike_eta_minutes"
            ),
            "bus_distance_km": route_data.get(
                "bus_distance_km"
            ),
            "bus_eta_minutes": route_data.get(
                "bus_eta_minutes"
            ),
            "bus_waiting_minutes": route_data.get(
                "bus_waiting_minutes"
            ),
            "estimated_minutes": route_data.get(
                "car_eta_minutes"
            ),
            "matching_stage": matching_stage,
            "distance_type": route_data.get(
                "distance_type",
                "road"
            ),
            "geometry": route_data.get(
                "geometry"
            ),
            "steps": route_data.get(
                "steps",
                []
            ),
            "already_responded": already_responded,
            "response_status": response_status,
            "details_unlocked": already_responded,
            "urgency_priority": urgency_priority
        }

        if already_responded:
            item.update({
                "patient_name": blood_request.patient_name,
                "patient_age": blood_request.patient_age,
                "units": blood_request.units,
                "hospital": blood_request.hospital,
                "additional_info": (
                    blood_request.additional_info
                ),
                "request_date": blood_request.created_at
            })

        nearby_requests.append(
            item
        )

    nearby_requests.sort(
        key=lambda item: (
            item["urgency_priority"],
            item["distance_km"]
        )
    )

    responded_request_ids = set(
        DonorResponse.objects
        .filter(
            donor=donor
        )
        .values_list(
            "blood_request_id",
            flat=True
        )
    )

    context.update({
        "requests_list": nearby_requests,
        "responded_request_ids": responded_request_ids,
        "status_filter": status_filter
    })

    return render(
        request,
        "donor/requests.html",
        context
    )


def respond_to_request(request, request_id):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method != "POST":
        return redirect("donor_requests")

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
        return redirect("login")

    try:
        blood_request = BloodRequest.objects.get(
            id=request_id,
            status__iexact="Active"
        )

    except BloodRequest.DoesNotExist:
        messages.error(
            request,
            (
                "Blood request not found or "
                "is no longer active."
            )
        )

        return redirect("donor_requests")

    donor_blood_group = (
        donor.blood_group or ""
    ).strip().upper()

    request_blood_group = (
        blood_request.blood_group or ""
    ).strip().upper()

    if donor_blood_group != request_blood_group:
        messages.error(
            request,
            (
                "You cannot respond to a request "
                "with a different blood group."
            )
        )

        return redirect("donor_requests")

    if (
        donor.latitude is None
        or donor.longitude is None
        or blood_request.latitude is None
        or blood_request.longitude is None
    ):
        messages.error(
            request,
            (
                "Both donor and request locations "
                "are required."
            )
        )

        return redirect("donor_requests")

    try:
        donor_latitude = float(
            donor.latitude
        )

        donor_longitude = float(
            donor.longitude
        )

        request_latitude = float(
            blood_request.latitude
        )

        request_longitude = float(
            blood_request.longitude
        )

    except (ValueError, TypeError):
        messages.error(
            request,
            "Invalid donor or request coordinates."
        )

        return redirect("donor_requests")

    if not validate_coordinates(
        donor_latitude,
        donor_longitude
    ):
        messages.error(
            request,
            "Donor location coordinates are invalid."
        )

        return redirect("donor_requests")

    if not validate_coordinates(
        request_latitude,
        request_longitude
    ):
        messages.error(
            request,
            (
                "Blood request location "
                "coordinates are invalid."
            )
        )

        return redirect("donor_requests")

    straight_distance = calculate_distance_km(
        donor_latitude,
        donor_longitude,
        request_latitude,
        request_longitude
    )

    if straight_distance is None:
        messages.error(
            request,
            "The GPS distance could not be calculated."
        )

        return redirect("donor_requests")

    route_data = get_road_distance_and_eta(
        donor_latitude,
        donor_longitude,
        request_latitude,
        request_longitude
    )

    if not route_data:
        messages.error(
            request,
            (
                "Road distance could not be calculated. "
                "Please try again."
            )
        )

        return redirect("donor_requests")

    distance_km = route_data.get(
        "road_distance_km"
    )

    if distance_km is None:
        messages.error(
            request,
            "Road distance is unavailable."
        )

        return redirect("donor_requests")

    try:
        distance_km = float(
            distance_km
        )

    except (ValueError, TypeError):
        messages.error(
            request,
            "Road distance is invalid."
        )

        return redirect("donor_requests")

    if distance_km > MAX_MATCH_DISTANCE_KM:
        messages.error(
            request,
            (
                f"This blood request is outside "
                f"the {MAX_MATCH_DISTANCE_KM:.0f} km "
                f"matching range."
            )
        )

        return redirect("donor_requests")

    existing_response = (
        DonorResponse.objects
        .filter(
            donor=donor,
            blood_request=blood_request
        )
        .order_by("-created_at")
        .first()
    )

    if existing_response:

        current_status = (
            existing_response.status or ""
        ).strip().lower()

        if current_status == "rejected":
            existing_response.status = "Responded"

            existing_response.save(
                update_fields=["status"]
            )

            messages.success(
                request,
                "Your response has been sent again."
            )

        else:
            messages.info(
                request,
                "You have already responded to this request."
            )

        return redirect("donor_requests")

    DonorResponse.objects.create(
        donor=donor,
        blood_request=blood_request,
        status="Accepted"
    )

    messages.success(
        request,
        (
            "Response sent successfully. "
            "Request details are now unlocked."
        )
    )

    return redirect("donor_requests")


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
        return redirect("login")

    history = (
        DonationHistory.objects
        .filter(
            donor=donor
        )
        .order_by(
            "-donation_date"
        )
    )

    context = {
        "name": user.name,
        "username": user.username,
        "donor": donor,
        "history": history
    }

    return render(
        request,
        "donor/history.html",
        context
    )


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
        return redirect("login")

    alerts = (
        BloodRequest.objects
        .filter(
            status__iexact="Active"
        )
        .order_by(
            "-created_at"
        )
    )

    context = {
        "name": user.name,
        "username": user.username,
        "alerts": alerts
    }

    return render(
        request,
        "donor/alerts.html",
        context
    )


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
        return redirect("login")

    active_requests = BloodRequest.objects.filter(
        needer=user,
        status__iexact="Active"
    )

    fulfilled_requests = BloodRequest.objects.filter(
        needer=user,
        status__iexact="Fulfilled"
    )

    response_count = (
        DonorResponse.objects
        .filter(
            blood_request__needer=user
        )
        .count()
    )

    active_count = active_requests.count()
    fulfilled_count = fulfilled_requests.count()

    active_request = (
        active_requests
        .order_by("-created_at")
        .first()
    )

    progress = 0

    if active_request:
        total_units = active_request.units or 0

        accepted_responses = (
            DonorResponse.objects
            .filter(
                blood_request=active_request,
                status__in=[
                    "Accepted",
                    "Completed"
                ]
            )
            .count()
        )

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
        "progress": progress
    }

    return render(
        request,
        "needer/needer_dashboard.html",
        context
    )


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
        return redirect("login")

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

        except (ValueError, TypeError):
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

        except (ValueError, TypeError):
            messages.error(
                request,
                "Blood units must be a valid number."
            )

            return redirect(
                "create_request"
            )

        latitude_value = None

        if latitude:
            try:
                latitude_value = float(
                    latitude
                )

                if not (
                    -90
                    <= latitude_value
                    <= 90
                ):
                    latitude_value = None

            except (ValueError, TypeError):
                latitude_value = None

        longitude_value = None

        if longitude:
            try:
                longitude_value = float(
                    longitude
                )

                if not (
                    -180
                    <= longitude_value
                    <= 180
                ):
                    longitude_value = None

            except (ValueError, TypeError):
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

    context = {
        "name": user.name,
        "username": user.username,
        "age": user.age,
        "role": user.role
    }

    return render(
        request,
        "needer/create_request.html",
        context
    )


def cancel_request(request, request_id):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method != "POST":
        return redirect("create_request")

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

    blood_request.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        "Blood request cancelled successfully."
    )

    return redirect(
        "create_request"
    )


def accept_donor_response(request, response_id):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method != "POST":
        return redirect("donor_requests")

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
        return redirect("login")

    try:
        donor_response = (
            DonorResponse.objects
            .select_related(
                "donor",
                "blood_request"
            )
            .get(
                id=response_id,
                donor=donor
            )
        )

    except DonorResponse.DoesNotExist:
        messages.error(
            request,
            "Response not found."
        )

        return redirect(
            "donor_requests"
        )

    blood_request = donor_response.blood_request

    if (
        str(
            blood_request.status
        ).strip().lower()
        != "active"
    ):
        messages.error(
            request,
            "This blood request is no longer active."
        )

        return redirect(
            "donor_requests"
        )

    current_status = (
        donor_response.status or ""
    ).strip().lower()

    if current_status == "accepted":
        messages.info(
            request,
            "You have already accepted this request."
        )

        return redirect(
            "donor_requests"
        )

    if current_status not in [
        "responded",
        "pending"
    ]:
        messages.error(
            request,
            (
                "This response cannot be accepted "
                "in its current state."
            )
        )

        return redirect(
            "donor_requests"
        )

    if (
        donor.blood_group or ""
    ).strip().upper() != (
        blood_request.blood_group or ""
    ).strip().upper():
        messages.error(
            request,
            "Blood group does not match this request."
        )

        return redirect(
            "donor_requests"
        )

    if (
        donor.latitude is None
        or donor.longitude is None
        or blood_request.latitude is None
        or blood_request.longitude is None
    ):
        messages.error(
            request,
            (
                "Both donor and request locations "
                "are required."
            )
        )

        return redirect(
            "donor_requests"
        )

    try:
        donor_latitude = float(
            donor.latitude
        )

        donor_longitude = float(
            donor.longitude
        )

        request_latitude = float(
            blood_request.latitude
        )

        request_longitude = float(
            blood_request.longitude
        )

    except (ValueError, TypeError):
        messages.error(
            request,
            "Invalid donor or request coordinates."
        )

        return redirect(
            "donor_requests"
        )

    if (
        not validate_coordinates(
            donor_latitude,
            donor_longitude
        )
        or not validate_coordinates(
            request_latitude,
            request_longitude
        )
    ):
        messages.error(
            request,
            "Invalid donor or request coordinates."
        )

        return redirect(
            "donor_requests"
        )

    route_data = get_road_distance_and_eta(
        donor_latitude,
        donor_longitude,
        request_latitude,
        request_longitude
    )

    if (
        not route_data
        or route_data.get(
            "road_distance_km"
        ) is None
    ):
        messages.error(
            request,
            "Road route could not be calculated."
        )

        return redirect(
            "donor_requests"
        )

    try:
        road_distance = float(
            route_data[
                "road_distance_km"
            ]
        )

    except (ValueError, TypeError):
        messages.error(
            request,
            "Road distance is invalid."
        )

        return redirect(
            "donor_requests"
        )

    if road_distance > MAX_MATCH_DISTANCE_KM:
        messages.error(
            request,
            (
                "This request is outside the "
                "allowed matching distance."
            )
        )

        return redirect(
            "donor_requests"
        )

    donor_response.status = "Accepted"

    donor_response.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        (
            "Request accepted successfully. "
            "The needy person can now see your route."
        )
    )

    return redirect(
        "donor_requests"
    )


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
        return redirect("login")

    requests_list = (
        BloodRequest.objects
        .filter(
            needer=user
        )
        .order_by(
            "-created_at"
        )
    )

    for blood_request in requests_list:

        blood_request.response_count = (
            DonorResponse.objects
            .filter(
                blood_request=blood_request
            )
            .count()
        )

        blood_request.accepted_count = (
            DonorResponse.objects
            .filter(
                blood_request=blood_request,
                status="Accepted"
            )
            .count()
        )

    selected_request = None

    request_id = request.GET.get(
        "request_id"
    )

    if request_id:
        try:
            selected_request = (
                BloodRequest.objects.get(
                    id=request_id,
                    needer=user
                )
            )

        except (
            BloodRequest.DoesNotExist,
            ValueError,
            TypeError
        ):
            selected_request = None

    if (
        selected_request is None
        and requests_list.exists()
    ):
        selected_request = requests_list.first()

    donor_responses = []

    response_count = 0
    accepted_count = 0
    pending_count = 0
    rejected_count = 0
    completed_count = 0

    accepted_donor_tracking = []

    tracking_colors = [
        "#0b3d91",
        "#7c3aed",
        "#00897b",
        "#ef6c00",
        "#c2185b"
    ]

    if selected_request:

        donor_responses = (
            DonorResponse.objects
            .filter(
                blood_request=selected_request
            )
            .select_related(
                "donor",
                "donor__user"
            )
            .order_by(
                "-created_at"
            )
        )

        response_count = (
            donor_responses.count()
        )

        accepted_count = (
            donor_responses
            .filter(
                status="Accepted"
            )
            .count()
        )

        pending_count = (
            donor_responses
            .filter(
                status__in=[
                    "Responded",
                    "Pending"
                ]
            )
            .count()
        )

        rejected_count = (
            donor_responses
            .filter(
                status="Rejected"
            )
            .count()
        )

        completed_count = (
            donor_responses
            .filter(
                status="Completed"
            )
            .count()
        )

        for response_index, response in enumerate(
            donor_responses
        ):

            donor = response.donor

            response.distance_km = None

            response.location_available = (
                donor.latitude is not None
                and donor.longitude is not None
            )

            response.normalized_status = (
                response.status
                or "Responded"
            ).strip()

            response.tracking_available = False
            response.can_track = False

            response.tracking_distance_km = None
            response.tracking_eta_minutes = None

            response.tracking_color = (
                tracking_colors[
                    response_index
                    % len(tracking_colors)
                ]
            )

            if (
                selected_request.latitude is not None
                and selected_request.longitude is not None
                and response.location_available
            ):

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

            if (
                response.status == "Accepted"
                and response.location_available
                and selected_request.latitude is not None
                and selected_request.longitude is not None
            ):

                donor_latitude = float(
                    donor.latitude
                )

                donor_longitude = float(
                    donor.longitude
                )

                request_latitude = float(
                    selected_request.latitude
                )

                request_longitude = float(
                    selected_request.longitude
                )

                if (
                    validate_coordinates(
                        donor_latitude,
                        donor_longitude
                    )
                    and validate_coordinates(
                        request_latitude,
                        request_longitude
                    )
                ):

                    route_data = get_road_distance_and_eta(
                        donor_latitude,
                        donor_longitude,
                        request_latitude,
                        request_longitude
                    )

                    if (
                        route_data
                        and route_data.get(
                            "geometry"
                        )
                    ):

                        road_distance = (
                            route_data.get(
                                "road_distance_km"
                            )
                        )

                        response.tracking_available = True
                        response.can_track = True

                        response.tracking_distance_km = (
                            round(
                                float(
                                    road_distance
                                ),
                                2
                            )
                            if road_distance is not None
                            else None
                        )

                        response.tracking_eta_minutes = (
                            route_data.get(
                                "car_eta_minutes"
                            )
                        )

                        accepted_donor_tracking.append({
                            "response_id": response.id,
                            "donor_id": donor.id,
                            "donor_name": (
                                donor.user.name
                                or "Donor"
                            ),
                            "latitude": donor_latitude,
                            "longitude": donor_longitude,
                            "request_latitude": request_latitude,
                            "request_longitude": request_longitude,
                            "road_distance_km": (
                                round(
                                    float(
                                        road_distance
                                    ),
                                    2
                                )
                                if road_distance is not None
                                else None
                            ),
                            "car_eta_minutes": (
                                route_data.get(
                                    "car_eta_minutes"
                                )
                            ),
                            "bike_eta_minutes": (
                                route_data.get(
                                    "bike_eta_minutes"
                                )
                            ),
                            "bus_eta_minutes": (
                                route_data.get(
                                    "bus_eta_minutes"
                                )
                            ),
                            "geometry": (
                                route_data.get(
                                    "geometry"
                                )
                            ),
                            "steps": (
                                route_data.get(
                                    "steps",
                                    []
                                )
                            ),
                            "color": (
                                response.tracking_color
                            )
                        })

    request_location_data = None

    if (
        selected_request
        and selected_request.latitude is not None
        and selected_request.longitude is not None
    ):
        request_location_data = {
            "latitude": float(
                selected_request.latitude
            ),
            "longitude": float(
                selected_request.longitude
            ),
            "label": (
                selected_request.location
                or "Blood Request Location"
            )
        }

    return render(
        request,
        "needer/find_donor.html",
        {
            "name": user.name,
            "username": user.username,
            "age": user.age,
            "role": user.role,
            "requests_list": requests_list,
            "selected_request": selected_request,
            "donor_responses": donor_responses,
            "response_count": response_count,
            "accepted_count": accepted_count,
            "pending_count": pending_count,
            "rejected_count": rejected_count,
            "completed_count": completed_count,
            "accepted_donor_tracking": (
                accepted_donor_tracking
            ),
            "request_location_data": (
                request_location_data
            )
        }
    )


def get_donor_tracking(request, request_id):
    if "user_id" not in request.session:
        return JsonResponse(
            {
                "success": False,
                "message": "Please login first."
            },
            status=401
        )

    try:
        user = LoginUser.objects.get(
            id=request.session.get("user_id"),
            role="needer"
        )

    except LoginUser.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "message": "Needer not found."
            },
            status=401
        )

    try:
        blood_request = BloodRequest.objects.get(
            id=request_id,
            needer=user
        )

    except BloodRequest.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "message": "Blood request not found."
            },
            status=404
        )

    if (
        blood_request.latitude is None
        or blood_request.longitude is None
    ):
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Blood request location "
                    "is unavailable."
                )
            },
            status=400
        )

    try:
        request_latitude = float(
            blood_request.latitude
        )

        request_longitude = float(
            blood_request.longitude
        )

    except (ValueError, TypeError):
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Invalid blood request "
                    "coordinates."
                )
            },
            status=400
        )

    if not validate_coordinates(
        request_latitude,
        request_longitude
    ):
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Invalid blood request "
                    "coordinates."
                )
            },
            status=400
        )

    colors = [
        "#0b3d91",
        "#7c3aed",
        "#00897b",
        "#ef6c00",
        "#c2185b"
    ]

    accepted_responses = (
        DonorResponse.objects
        .filter(
            blood_request=blood_request,
            status="Accepted"
        )
        .select_related(
            "donor",
            "donor__user"
        )
        .order_by(
            "created_at"
        )
    )

    donors = []

    for index, response in enumerate(
        accepted_responses
    ):

        donor = response.donor

        color = colors[
            index % len(colors)
        ]

        base = {
            "response_id": response.id,
            "donor_id": donor.id,
            "donor_name": (
                donor.user.name
                or "Donor"
            ),
            "color": color
        }

        if (
            donor.latitude is None
            or donor.longitude is None
        ):
            base.update({
                "location_available": False,
                "route_available": False,
                "message": (
                    "Donor location is unavailable."
                )
            })

            donors.append(
                base
            )

            continue

        try:
            donor_latitude = float(
                donor.latitude
            )

            donor_longitude = float(
                donor.longitude
            )

        except (ValueError, TypeError):
            base.update({
                "location_available": False,
                "route_available": False,
                "message": (
                    "Donor coordinates are invalid."
                )
            })

            donors.append(
                base
            )

            continue

        if not validate_coordinates(
            donor_latitude,
            donor_longitude
        ):
            base.update({
                "location_available": False,
                "route_available": False,
                "message": (
                    "Donor coordinates are invalid."
                )
            })

            donors.append(
                base
            )

            continue

        route_data = get_road_distance_and_eta(
            donor_latitude,
            donor_longitude,
            request_latitude,
            request_longitude
        )

        if not route_data:
            base.update({
                "location_available": True,
                "route_available": False,
                "latitude": donor_latitude,
                "longitude": donor_longitude,
                "message": (
                    "Road route is temporarily "
                    "unavailable."
                )
            })

            donors.append(
                base
            )

            continue

        base.update({
            "location_available": True,
            "route_available": bool(
                route_data.get(
                    "geometry"
                )
            ),
            "latitude": donor_latitude,
            "longitude": donor_longitude,
            "road_distance_km": (
                route_data.get(
                    "road_distance_km"
                )
            ),
            "car_eta_minutes": (
                route_data.get(
                    "car_eta_minutes"
                )
            ),
            "bike_eta_minutes": (
                route_data.get(
                    "bike_eta_minutes"
                )
            ),
            "bus_eta_minutes": (
                route_data.get(
                    "bus_eta_minutes"
                )
            ),
            "geometry": (
                route_data.get(
                    "geometry"
                )
            ),
            "steps": (
                route_data.get(
                    "steps",
                    []
                )
            )
        })

        donors.append(
            base
        )

    return JsonResponse({
        "success": True,
        "request_id": blood_request.id,
        "request_location": {
            "latitude": request_latitude,
            "longitude": request_longitude,
            "label": (
                blood_request.location
                or "Blood Request Location"
            )
        },
        "accepted_donors": donors
    })


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
        return redirect("login")

    total_users = LoginUser.objects.count()

    total_donors = (
        LoginUser.objects
        .filter(
            role="donor"
        )
        .count()
    )

    total_needers = (
        LoginUser.objects
        .filter(
            role="needer"
        )
        .count()
    )

    total_requests = (
        BloodRequest.objects.count()
    )

    active_requests = (
        BloodRequest.objects
        .filter(
            status="Active"
        )
        .count()
    )

    fulfilled_requests = (
        BloodRequest.objects
        .filter(
            status="Fulfilled"
        )
        .count()
    )

    context = {
        "name": user.name,
        "username": user.username,
        "total_users": total_users,
        "total_donors": total_donors,
        "total_needers": total_needers,
        "total_requests": total_requests,
        "active_requests": active_requests,
        "fulfilled_requests": fulfilled_requests
    }

    return render(
        request,
        "admin/admin_dashboard.html",
        context
    )


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
        return redirect("login")

    users = (
        LoginUser.objects
        .exclude(
            role="admin"
        )
        .order_by(
            "-id"
        )
    )

    context = {
        "name": admin.name,
        "username": admin.username,
        "users": users
    }

    return render(
        request,
        "admin/admin_users.html",
        context
    )


def admin_verify_user(request, user_id):
    if "user_id" not in request.session:
        return redirect("login")

    try:
        LoginUser.objects.get(
            id=request.session.get(
                "user_id"
            ),
            role="admin"
        )

        user = LoginUser.objects.get(
            id=user_id
        )

    except LoginUser.DoesNotExist:
        return redirect("login")

    user.is_verified = True

    user.save(
        update_fields=["is_verified"]
    )

    messages.success(
        request,
        "User verified successfully."
    )

    return redirect(
        "admin_users"
    )


def admin_block_user(request, user_id):
    if "user_id" not in request.session:
        return redirect("login")

    try:
        LoginUser.objects.get(
            id=request.session.get(
                "user_id"
            ),
            role="admin"
        )

        user = LoginUser.objects.get(
            id=user_id
        )

    except LoginUser.DoesNotExist:
        return redirect("login")

    user.is_blocked = True

    user.save(
        update_fields=["is_blocked"]
    )

    messages.success(
        request,
        "User blocked successfully."
    )

    return redirect(
        "admin_users"
    )


def admin_unblock_user(request, user_id):
    if "user_id" not in request.session:
        return redirect("login")

    try:
        LoginUser.objects.get(
            id=request.session.get(
                "user_id"
            ),
            role="admin"
        )

        user = LoginUser.objects.get(
            id=user_id
        )

    except LoginUser.DoesNotExist:
        return redirect("login")

    user.is_blocked = False

    user.save(
        update_fields=["is_blocked"]
    )

    messages.success(
        request,
        "User unblocked successfully."
    )

    return redirect(
        "admin_users"
    )


def admin_sos(request):
    if "user_id" not in request.session:
        return redirect("login")

    try:
        admin = LoginUser.objects.get(
            id=request.session.get(
                "user_id"
            ),
            role="admin"
        )

    except LoginUser.DoesNotExist:
        return redirect("login")

    sos_requests = (
        BloodRequest.objects
        .filter(
            urgency="Emergency",
            status="Active"
        )
        .order_by(
            "-created_at"
        )
    )

    context = {
        "name": admin.name,
        "username": admin.username,
        "sos_requests": sos_requests
    }

    return render(
        request,
        "admin/admin_sos.html",
        context
    )


def admin_analytics(request):
    if "user_id" not in request.session:
        return redirect("login")

    try:
        admin = LoginUser.objects.get(
            id=request.session.get(
                "user_id"
            ),
            role="admin"
        )

    except LoginUser.DoesNotExist:
        return redirect("login")

    total_donors = (
        LoginUser.objects
        .filter(
            role="donor"
        )
        .count()
    )

    total_needers = (
        LoginUser.objects
        .filter(
            role="needer"
        )
        .count()
    )

    total_requests = (
        BloodRequest.objects.count()
    )

    fulfilled_requests = (
        BloodRequest.objects
        .filter(
            status="Fulfilled"
        )
        .count()
    )

    context = {
        "name": admin.name,
        "username": admin.username,
        "total_donors": total_donors,
        "total_needers": total_needers,
        "total_requests": total_requests,
        "fulfilled_requests": fulfilled_requests
    }

    return render(
        request,
        "admin/admin_analytics.html",
        context
    )


def logout_user(request):
    request.session.flush()
    return redirect("login")


def get_needer_donor_route(request, response_id):
    if "user_id" not in request.session:
        return JsonResponse(
            {
                "success": False,
                "error": "Please login first."
            },
            status=401
        )

    try:
        user = LoginUser.objects.get(
            id=request.session.get(
                "user_id"
            ),
            role="needer"
        )

    except LoginUser.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "error": "Needer account not found."
            },
            status=401
        )

    try:
        donor_response = (
            DonorResponse.objects
            .select_related(
                "donor",
                "donor__user",
                "blood_request",
                "blood_request__needer"
            )
            .get(
                id=response_id,
                status="Accepted"
            )
        )

    except DonorResponse.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Accepted donor response "
                    "not found."
                )
            },
            status=404
        )

    blood_request = donor_response.blood_request

    if blood_request.needer_id != user.id:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "You are not authorized to "
                    "view this donor route."
                )
            },
            status=403
        )

    donor = donor_response.donor

    if donor is None:
        return JsonResponse(
            {
                "success": False,
                "error": "Donor profile not found."
            },
            status=404
        )

    if (
        donor.latitude is None
        or donor.longitude is None
    ):
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Donor location is unavailable."
                )
            },
            status=400
        )

    if (
        blood_request.latitude is None
        or blood_request.longitude is None
    ):
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Blood request location "
                    "is unavailable."
                )
            },
            status=400
        )

    try:
        donor_latitude = float(
            donor.latitude
        )

        donor_longitude = float(
            donor.longitude
        )

        request_latitude = float(
            blood_request.latitude
        )

        request_longitude = float(
            blood_request.longitude
        )

    except (ValueError, TypeError):
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Invalid location coordinates."
                )
            },
            status=400
        )

    if not validate_coordinates(
        donor_latitude,
        donor_longitude
    ):
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Donor coordinates are invalid."
                )
            },
            status=400
        )

    if not validate_coordinates(
        request_latitude,
        request_longitude
    ):
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Blood request coordinates "
                    "are invalid."
                )
            },
            status=400
        )

    route_data = get_road_distance_and_eta(
        donor_latitude,
        donor_longitude,
        request_latitude,
        request_longitude
    )

    if not route_data:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Road route could not "
                    "be calculated."
                )
            },
            status=503
        )

    return JsonResponse({
        "success": True,
        "response_id": donor_response.id,
        "donor": {
            "id": donor.id,
            "user_id": (
                donor.user.id
                if donor.user
                else None
            ),
            "name": (
                donor.user.name
                if donor.user
                else "Donor"
            ),
            "blood_group": donor.blood_group,
            "latitude": donor_latitude,
            "longitude": donor_longitude
        },
        "destination": {
            "latitude": request_latitude,
            "longitude": request_longitude
        },
        "road_distance_km": (
            route_data.get(
                "road_distance_km"
            )
        ),
        "car_distance_km": (
            route_data.get(
                "car_distance_km"
            )
        ),
        "car_eta_minutes": (
            route_data.get(
                "car_eta_minutes"
            )
        ),
        "bike_distance_km": (
            route_data.get(
                "bike_distance_km"
            )
        ),
        "bike_eta_minutes": (
            route_data.get(
                "bike_eta_minutes"
            )
        ),
        "bus_distance_km": (
            route_data.get(
                "bus_distance_km"
            )
        ),
        "bus_eta_minutes": (
            route_data.get(
                "bus_eta_minutes"
            )
        ),
        "bus_waiting_minutes": (
            route_data.get(
                "bus_waiting_minutes"
            )
        ),
        "distance_type": (
            route_data.get(
                "distance_type"
            )
        ),
        "geometry": (
            route_data.get(
                "geometry"
            )
        ),
        "steps": (
            route_data.get(
                "steps",
                []
            )
        )
    })
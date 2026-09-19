# services/matching.py

from .distance import (
    calculate_distance_km,
    validate_coordinates,
)

from .eta import (
    get_all_eta,
)


# Maximum distance allowed for donor matching.
MAX_MATCH_DISTANCE_KM = 15.0


# Urgency priority.
# Lower number = higher priority.
URGENCY_PRIORITY = {
    "Emergency": 1,
    "Urgent": 2,
    "Normal": 3,
}


def get_urgency_priority(urgency):
    """
    Return numerical priority for request urgency.
    """

    return URGENCY_PRIORITY.get(
        str(urgency),
        99
    )


def is_blood_group_match(
    donor_blood_group,
    request_blood_group
):
    """
    HemoHub currently uses exact blood-group matching.

    Example:
        O+ -> O+ = True
        O+ -> A+ = False
    """

    if not donor_blood_group:
        return False

    if not request_blood_group:
        return False

    return (
        str(donor_blood_group).strip().upper()
        ==
        str(request_blood_group).strip().upper()
    )


def get_match_stage(distance_km):
    """
    Divide nearby requests into distance stages.
    """

    if distance_km is None:
        return None

    if distance_km <= 5:
        return "Stage 1"

    if distance_km <= 10:
        return "Stage 2"

    if distance_km <= 15:
        return "Stage 3"

    return None


def build_request_match(
    donor,
    blood_request
):
    """
    Build a safe matching result for one blood request.

    Returns:
        Dictionary containing matching information,
        or None if the request does not qualify.
    """

    # --------------------------------------------------
    # 1. DONOR BLOOD GROUP
    # --------------------------------------------------

    donor_blood_group = getattr(
        donor,
        "blood_group",
        None
    )

    # --------------------------------------------------
    # 2. REQUEST BLOOD GROUP
    # --------------------------------------------------

    request_blood_group = getattr(
        blood_request,
        "blood_group",
        None
    )

    # --------------------------------------------------
    # 3. BLOOD GROUP MATCH
    # --------------------------------------------------

    if not is_blood_group_match(
        donor_blood_group,
        request_blood_group
    ):
        return None

    # --------------------------------------------------
    # 4. DONOR COORDINATES
    # --------------------------------------------------

    donor_latitude = getattr(
        donor,
        "latitude",
        None
    )

    donor_longitude = getattr(
        donor,
        "longitude",
        None
    )

    # --------------------------------------------------
    # 5. REQUEST COORDINATES
    # --------------------------------------------------

    request_latitude = getattr(
        blood_request,
        "latitude",
        None
    )

    request_longitude = getattr(
        blood_request,
        "longitude",
        None
    )

    # --------------------------------------------------
    # 6. VALIDATE GPS
    # --------------------------------------------------

    if not validate_coordinates(
        donor_latitude,
        donor_longitude
    ):
        return None

    if not validate_coordinates(
        request_latitude,
        request_longitude
    ):
        return None

    # --------------------------------------------------
    # 7. CALCULATE DISTANCE
    # --------------------------------------------------

    distance_km = calculate_distance_km(
        donor_latitude,
        donor_longitude,
        request_latitude,
        request_longitude
    )

    if distance_km is None:
        return None

    # --------------------------------------------------
    # 8. MAXIMUM MATCHING DISTANCE
    # --------------------------------------------------

    if distance_km > MAX_MATCH_DISTANCE_KM:
        return None

    # --------------------------------------------------
    # 9. ETA
    # --------------------------------------------------

    eta = get_all_eta(distance_km)

    # --------------------------------------------------
    # 10. URGENCY
    # --------------------------------------------------

    urgency = getattr(
        blood_request,
        "urgency",
        "Normal"
    )

    urgency_priority = get_urgency_priority(
        urgency
    )

    # --------------------------------------------------
    # 11. STAGE
    # --------------------------------------------------

    stage = get_match_stage(
        distance_km
    )

    # --------------------------------------------------
    # 12. SAFE MATCH DATA
    # --------------------------------------------------

    return {
        "request": blood_request,

        "distance_km": distance_km,

        "stage": stage,

        "urgency": urgency,

        "urgency_priority": urgency_priority,

        "car_eta_minutes": eta[
            "car_eta_minutes"
        ],

        "bike_eta_minutes": eta[
            "bike_eta_minutes"
        ],
    }


def sort_matches(matches):
    """
    Sort requests by:

    1. Emergency
    2. Urgent
    3. Normal
    4. Shortest distance
    """

    return sorted(
        matches,
        key=lambda item: (
            item.get(
                "urgency_priority",
                99
            ),
            item.get(
                "distance_km",
                float("inf")
            )
        )
    )


def find_matching_requests(
    donor,
    requests
):
    """
    Find all matching blood requests for a donor.

    Args:
        donor: DonorProfile object.
        requests: queryset/list of BloodRequest objects.

    Returns:
        Sorted list of matching request dictionaries.
    """

    matches = []

    for blood_request in requests:

        result = build_request_match(
            donor,
            blood_request
        )

        if result is not None:
            matches.append(result)

    return sort_matches(matches)
# services/eta.py


# Average travel speeds.
# These are intentionally configurable so you can
# change them later without changing the matching logic.

TRAVEL_SPEEDS = {
    "car": 35,
    "bike": 30,
}


def calculate_eta_minutes(distance_km, mode="car"):
    """
    Calculate estimated travel time.

    Args:
        distance_km: Distance in kilometers.
        mode: car or bike.

    Returns:
        Estimated travel time in minutes.
    """

    if distance_km is None:
        return None

    try:
        distance_km = float(distance_km)
    except (TypeError, ValueError):
        return None

    if distance_km < 0:
        return None

    mode = str(mode).lower()

    speed_kmh = TRAVEL_SPEEDS.get(mode)

    if speed_kmh is None:
        return None

    if distance_km == 0:
        return 0

    eta_minutes = (distance_km / speed_kmh) * 60

    return max(1, round(eta_minutes))


def get_all_eta(distance_km):
    """
    Return ETA estimates for all supported travel modes.
    """

    return {
        "car_eta_minutes": calculate_eta_minutes(
            distance_km,
            "car"
        ),

        "bike_eta_minutes": calculate_eta_minutes(
            distance_km,
            "bike"
        ),
    }


def format_eta(minutes):
    """
    Convert ETA minutes into a user-friendly string.
    """

    if minutes is None:
        return "Unavailable"

    minutes = int(minutes)

    if minutes < 1:
        return "Less than 1 min"

    if minutes == 1:
        return "1 min"

    if minutes < 60:
        return f"{minutes} mins"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if remaining_minutes == 0:
        return f"{hours} hr"

    return f"{hours} hr {remaining_minutes} mins"
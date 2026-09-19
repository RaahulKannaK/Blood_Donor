# services/distance.py

import math


def validate_coordinates(latitude, longitude):
    """
    Validate latitude and longitude values.

    Returns:
        True  -> valid coordinates
        False -> invalid coordinates
    """

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return False

    if not (-90 <= latitude <= 90):
        return False

    if not (-180 <= longitude <= 180):
        return False

    # Reject 0,0 because it is normally an invalid/missing GPS location
    if latitude == 0 and longitude == 0:
        return False

    return True


def calculate_distance_km(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):
    """
    Calculate the straight-line geographic distance
    between two GPS coordinates using the Haversine formula.

    Returns:
        Distance in kilometers.
        None if coordinates are invalid.
    """

    if not all([
        validate_coordinates(latitude1, longitude1),
        validate_coordinates(latitude2, longitude2)
    ]):
        return None

    latitude1 = float(latitude1)
    longitude1 = float(longitude1)
    latitude2 = float(latitude2)
    longitude2 = float(longitude2)

    # Convert degrees to radians
    lat1 = math.radians(latitude1)
    lon1 = math.radians(longitude1)

    lat2 = math.radians(latitude2)
    lon2 = math.radians(longitude2)

    # Differences
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    # Protect against tiny floating-point errors
    a = min(1.0, max(0.0, a))

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    # Earth's mean radius
    earth_radius_km = 6371.0088

    distance = earth_radius_km * c

    return round(distance, 2)
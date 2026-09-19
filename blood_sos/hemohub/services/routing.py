
import requests
import math


# ============================================================
# HEMOHUB ROUTING CONFIGURATION
# ============================================================

# Public OSRM routing server.
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

# Maximum request timeout.
ROUTING_TIMEOUT = 10

# Ask OSRM for alternative routes.
# We will select the route with the smallest road distance.
OSRM_ALTERNATIVES = 3

# HemoHub approximate transport speeds.
# These are used for estimated bike/bus ETA.
BIKE_AVERAGE_SPEED_KMH = 28
BUS_AVERAGE_SPEED_KMH = 22

# Approximate bus waiting/boarding time.
BUS_WAITING_MINUTES = 5


# ============================================================
# COORDINATE VALIDATION
# ============================================================

def validate_coordinates(latitude, longitude):

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return False

    if not (-90 <= latitude <= 90):
        return False

    if not (-180 <= longitude <= 180):
        return False

    return True


# ============================================================
# GPS / HAVERSINE DISTANCE
# ============================================================

def calculate_gps_distance_km(
    start_latitude,
    start_longitude,
    end_latitude,
    end_longitude
):

    if not validate_coordinates(
        start_latitude,
        start_longitude
    ):
        return None

    if not validate_coordinates(
        end_latitude,
        end_longitude
    ):
        return None

    try:

        lat1 = math.radians(float(start_latitude))
        lon1 = math.radians(float(start_longitude))

        lat2 = math.radians(float(end_latitude))
        lon2 = math.radians(float(end_longitude))

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            +
            math.cos(lat1)
            * math.cos(lat2)
            * math.sin(dlon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )

        earth_radius_km = 6371.0

        distance = earth_radius_km * c

        return round(distance, 2)

    except Exception as e:

        print(
            "❌ GPS distance calculation error:",
            e
        )

        return None


# ============================================================
# OSRM ROAD ROUTE
# ============================================================

def get_osrm_route(
    start_latitude,
    start_longitude,
    end_latitude,
    end_longitude
):

    print("\n🛣️ OSRM SHORTEST-AVAILABLE ROAD ROUTING")

    if not validate_coordinates(
        start_latitude,
        start_longitude
    ):
        print("❌ Invalid starting coordinates.")
        return None

    if not validate_coordinates(
        end_latitude,
        end_longitude
    ):
        print("❌ Invalid destination coordinates.")
        return None

    # --------------------------------------------------------
    # IMPORTANT:
    # OSRM requires longitude,latitude
    # --------------------------------------------------------

    coordinates = (
        f"{float(start_longitude)},{float(start_latitude)};"
        f"{float(end_longitude)},{float(end_latitude)}"
    )

    url = f"{OSRM_URL}/{coordinates}"

    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "true",

        # Ask OSRM for alternative routes.
        # We will select the shortest-distance route ourselves.
        "alternatives": OSRM_ALTERNATIVES
    }

    print("🌐 Routing URL:")
    print(url)

    print(
        "🔀 Requested OSRM alternatives:",
        OSRM_ALTERNATIVES
    )

    try:

        response = requests.get(
            url,
            params=params,
            timeout=ROUTING_TIMEOUT
        )

        print(
            "🌐 OSRM HTTP Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "❌ OSRM request failed:",
                response.status_code
            )

            return None

        data = response.json()

        if data.get("code") != "Ok":

            print(
                "❌ OSRM route error:",
                data.get("code")
            )

            return None

        routes = data.get("routes", [])

        if not routes:

            print(
                "❌ OSRM returned no routes."
            )

            return None

        # ----------------------------------------------------
        # SELECT SHORTEST ROAD DISTANCE
        # ----------------------------------------------------

        valid_routes = []

        for index, candidate_route in enumerate(routes):

            distance_meters = candidate_route.get(
                "distance"
            )

            if distance_meters is None:
                continue

            try:

                distance_meters = float(
                    distance_meters
                )

                valid_routes.append(
                    (
                        distance_meters,
                        index,
                        candidate_route
                    )
                )

            except (TypeError, ValueError):

                continue

        if not valid_routes:

            print(
                "❌ No valid route distances returned."
            )

            return None

        # Smallest road distance wins.
        valid_routes.sort(
            key=lambda item: item[0]
        )

        shortest_distance_meters = (
            valid_routes[0][0]
        )

        selected_route_index = (
            valid_routes[0][1]
        )

        route = valid_routes[0][2]

        print(
            "🔀 OSRM Routes Returned:",
            len(routes)
        )

        print(
            "🏁 Selected Route Index:",
            selected_route_index
        )

        # ----------------------------------------------------
        # PRINT ALL AVAILABLE ROUTES
        # ----------------------------------------------------

        for (
            route_distance,
            route_index,
            _
        ) in valid_routes:

            print(
                f"   Route {route_index + 1}: "
                f"{route_distance / 1000:.2f} km"
            )

        # ----------------------------------------------------
        # DISTANCE
        # ----------------------------------------------------

        road_distance_km = (
            shortest_distance_meters / 1000
        )

        road_distance_km = round(
            road_distance_km,
            2
        )

        # ----------------------------------------------------
        # CAR ETA
        # ----------------------------------------------------

        duration_seconds = route.get(
            "duration"
        )

        if duration_seconds is not None:

            car_eta_minutes = max(
                1,
                round(
                    float(duration_seconds) / 60
                )
            )

        else:

            car_eta_minutes = None

        # ----------------------------------------------------
        # ROUTE GEOMETRY
        # ----------------------------------------------------

        geometry = route.get(
            "geometry"
        )

        if geometry:

            print(
                "🗺️ Selected route geometry: AVAILABLE"
            )

        else:

            print(
                "⚠️ Selected route geometry: MISSING"
            )

        # ----------------------------------------------------
        # ROUTE STEPS
        # ----------------------------------------------------

        legs = route.get(
            "legs",
            []
        )

        steps = (
            legs[0].get("steps", [])
            if legs
            else []
        )

        print(
            "🧭 Selected route steps:",
            len(steps)
        )

        # ----------------------------------------------------
        # FINAL ROUTE INFORMATION
        # ----------------------------------------------------

        print(
            "🛣️ Shortest available OSRM road distance:",
            road_distance_km,
            "km"
        )

        print(
            "🚗 Selected route car ETA:",
            car_eta_minutes,
            "minutes"
        )

        return {
            "road_distance_km": road_distance_km,
            "car_eta_minutes": car_eta_minutes,
            "geometry": geometry,
            "steps": steps,

            # Useful for debugging.
            "route_count": len(routes),
            "selected_route_index": selected_route_index
        }

    except requests.exceptions.Timeout:

        print(
            "❌ OSRM request timed out."
        )

        return None

    except requests.exceptions.RequestException as e:

        print(
            "❌ OSRM connection error:",
            e
        )

        return None

    except Exception as e:

        print(
            "❌ OSRM unexpected error:",
            e
        )

        return None


# ============================================================
# BIKE ETA
# ============================================================

def calculate_bike_eta(distance_km):

    if distance_km is None:
        return None

    try:

        eta = (
            float(distance_km)
            / BIKE_AVERAGE_SPEED_KMH
        ) * 60

        return max(
            1,
            round(eta)
        )

    except Exception as e:

        print(
            "❌ Bike ETA calculation error:",
            e
        )

        return None


# ============================================================
# BUS ETA
# ============================================================

def calculate_bus_eta(distance_km):

    if distance_km is None:
        return None

    try:

        travel_minutes = (
            float(distance_km)
            / BUS_AVERAGE_SPEED_KMH
        ) * 60

        total_minutes = (
            travel_minutes
            + BUS_WAITING_MINUTES
        )

        return max(
            5,
            round(total_minutes)
        )

    except Exception as e:

        print(
            "❌ Bus ETA calculation error:",
            e
        )

        return None


# ============================================================
# COMPLETE ROUTING
# ============================================================

def get_road_distance_and_eta(
    start_latitude,
    start_longitude,
    end_latitude,
    end_longitude
):

    print("\n" + "=" * 60)
    print("🛣️ HEMOHUB ROAD ROUTING STARTED")
    print("=" * 60)

    # --------------------------------------------------------
    # GPS GEOGRAPHIC DISTANCE
    # --------------------------------------------------------

    gps_distance = calculate_gps_distance_km(
        start_latitude,
        start_longitude,
        end_latitude,
        end_longitude
    )

    print(
        "📏 GPS Geographic Distance:",
        gps_distance,
        "km"
    )

    # --------------------------------------------------------
    # SHORTEST AVAILABLE OSRM ROAD ROUTE
    # --------------------------------------------------------

    route = get_osrm_route(
        start_latitude,
        start_longitude,
        end_latitude,
        end_longitude
    )

    if route is None:

        print(
            "❌ Road route unavailable."
        )

        return None

    # --------------------------------------------------------
    # USE SELECTED SHORTEST ROUTE
    # --------------------------------------------------------

    road_distance = route[
        "road_distance_km"
    ]

    car_eta = route[
        "car_eta_minutes"
    ]

    geometry = route.get(
        "geometry"
    )

    steps = route.get(
        "steps",
        []
    )

    # --------------------------------------------------------
    # ESTIMATED TRANSPORT ETAs
    # --------------------------------------------------------

    bike_eta = calculate_bike_eta(
        road_distance
    )

    bus_eta = calculate_bus_eta(
        road_distance
    )

    # --------------------------------------------------------
    # LOGGING
    # --------------------------------------------------------

    print(
        "📍 Final Shortest Road Distance:",
        road_distance,
        "km"
    )

    print(
        "🚗 Final Car ETA:",
        car_eta,
        "minutes"
    )

    print(
        "🏍️ Final Bike ETA:",
        bike_eta,
        "minutes"
    )

    print(
        "🚌 Estimated Bus ETA:",
        bus_eta,
        "minutes"
    )

    print(
        "🗺️ Geometry:",
        "AVAILABLE" if geometry else "MISSING"
    )

    print(
        "🧭 Steps:",
        len(steps)
    )

    print("=" * 60)

    # --------------------------------------------------------
    # IMPORTANT:
    # The SAME road_distance is now used for matching,
    # and the SAME geometry is used for Leaflet.
    # --------------------------------------------------------

    return {
        "gps_distance_km": gps_distance,

        "road_distance_km": road_distance,

        "car_distance_km": road_distance,
        "car_eta_minutes": car_eta,

        "bike_distance_km": road_distance,
        "bike_eta_minutes": bike_eta,

        "bus_distance_km": road_distance,
        "bus_eta_minutes": bus_eta,

        "bus_waiting_minutes": BUS_WAITING_MINUTES,

        "distance_type": (
            "Shortest available OSRM road distance"
        ),

        "geometry": geometry,
        "steps": steps,

        "route_count": route.get(
            "route_count"
        ),

        "selected_route_index": route.get(
            "selected_route_index"
        )
    }


# ============================================================
# COMPATIBILITY FUNCTIONS
# ============================================================

def get_car_route(
    start_latitude,
    start_longitude,
    end_latitude,
    end_longitude
):

    result = get_road_distance_and_eta(
        start_latitude,
        start_longitude,
        end_latitude,
        end_longitude
    )

    if result is None:
        return None, None

    return (
        result["road_distance_km"],
        result["car_eta_minutes"]
    )


def get_bike_route(
    start_latitude,
    start_longitude,
    end_latitude,
    end_longitude
):

    result = get_road_distance_and_eta(
        start_latitude,
        start_longitude,
        end_latitude,
        end_longitude
    )

    if result is None:
        return None, None

    return (
        result["road_distance_km"],
        result["bike_eta_minutes"]
    )


def get_bus_eta(
    start_latitude,
    start_longitude,
    end_latitude,
    end_longitude
):

    result = get_road_distance_and_eta(
        start_latitude,
        start_longitude,
        end_latitude,
        end_longitude
    )

    if result is None:
        return None, None

    return (
        result["road_distance_km"],
        result["bus_eta_minutes"]
    )

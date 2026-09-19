
import requests
import math


# ============================================================
# HEMOHUB ROUTING CONFIGURATION
# ============================================================

# Public OSRM routing server.
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

# Maximum time allowed for OSRM response.
# Increased from 10 seconds because cloud-to-public-API
# connections can sometimes take longer than local requests.
ROUTING_TIMEOUT = 20

# Ask OSRM for alternative routes.
# HemoHub will select the route with the smallest road distance.
OSRM_ALTERNATIVES = 3

# HemoHub approximate transport speeds.
# These are used for estimated bike/bus ETA.
BIKE_AVERAGE_SPEED_KMH = 28
BUS_AVERAGE_SPEED_KMH = 22

# Approximate bus waiting/boarding time.
BUS_WAITING_MINUTES = 5

# ------------------------------------------------------------
# HTTP HEADERS
# ------------------------------------------------------------
# Identifies HemoHub when accessing the public OSRM service.
# This is especially useful when running from cloud hosting.
OSRM_HEADERS = {
    "User-Agent": (
        "HemoHub-BloodDonation-System/1.0 "
        "(Django routing service)"
    ),
    "Accept": "application/json",
}


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

        lat1 = math.radians(
            float(start_latitude)
        )

        lon1 = math.radians(
            float(start_longitude)
        )

        lat2 = math.radians(
            float(end_latitude)
        )

        lon2 = math.radians(
            float(end_longitude)
        )

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

        return round(
            distance,
            2
        )

    except Exception as e:

        print(
            "=" * 60
        )

        print(
            "❌ GPS DISTANCE CALCULATION ERROR"
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            repr(e)
        )

        print(
            "=" * 60
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

    print("\n" + "=" * 60)
    print("🛣️ OSRM SHORTEST-AVAILABLE ROAD ROUTING")
    print("=" * 60)

    # --------------------------------------------------------
    # VALIDATE STARTING COORDINATES
    # --------------------------------------------------------

    if not validate_coordinates(
        start_latitude,
        start_longitude
    ):

        print(
            "❌ Invalid starting coordinates."
        )

        print(
            "START:",
            start_latitude,
            start_longitude
        )

        return None

    # --------------------------------------------------------
    # VALIDATE DESTINATION COORDINATES
    # --------------------------------------------------------

    if not validate_coordinates(
        end_latitude,
        end_longitude
    ):

        print(
            "❌ Invalid destination coordinates."
        )

        print(
            "DESTINATION:",
            end_latitude,
            end_longitude
        )

        return None

    # --------------------------------------------------------
    # CONVERT FLOAT VALUES
    # --------------------------------------------------------

    try:

        start_latitude = float(
            start_latitude
        )

        start_longitude = float(
            start_longitude
        )

        end_latitude = float(
            end_latitude
        )

        end_longitude = float(
            end_longitude
        )

    except (TypeError, ValueError) as e:

        print(
            "❌ Coordinate conversion failed:",
            repr(e)
        )

        return None

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # OSRM requires:
    #
    # longitude,latitude
    #
    # NOT:
    #
    # latitude,longitude
    # --------------------------------------------------------

    coordinates = (
        f"{start_longitude},{start_latitude};"
        f"{end_longitude},{end_latitude}"
    )

    url = f"{OSRM_URL}/{coordinates}"

    # --------------------------------------------------------
    # OSRM PARAMETERS
    # --------------------------------------------------------

    params = {

        # Return complete route geometry.
        "overview": "full",

        # GeoJSON geometry for Leaflet.
        "geometries": "geojson",

        # Turn-by-turn route steps.
        "steps": "true",

        # Request alternative routes.
        "alternatives": OSRM_ALTERNATIVES,
    }

    # --------------------------------------------------------
    # LOG REQUEST INFORMATION
    # --------------------------------------------------------

    print(
        "🌐 OSRM URL:"
    )

    print(
        url
    )

    print(
        "🌐 OSRM PARAMETERS:"
    )

    print(
        params
    )

    print(
        "🔀 Requested alternatives:",
        OSRM_ALTERNATIVES
    )

    print(
        "⏱️ Request timeout:",
        ROUTING_TIMEOUT,
        "seconds"
    )

    print(
        "📍 START:",
        start_latitude,
        start_longitude
    )

    print(
        "📍 DESTINATION:",
        end_latitude,
        end_longitude
    )

    print(
        "🌐 User-Agent:",
        OSRM_HEADERS.get("User-Agent")
    )

    # ========================================================
    # CALL OSRM
    # ========================================================

    try:

        print(
            "\n📡 Sending request to OSRM..."
        )

        response = requests.get(

            url,

            params=params,

            headers=OSRM_HEADERS,

            timeout=ROUTING_TIMEOUT
        )

        # ----------------------------------------------------
        # HTTP RESPONSE INFORMATION
        # ----------------------------------------------------

        print(
            "🌐 OSRM HTTP STATUS:",
            response.status_code
        )

        print(
            "🌐 OSRM RESPONSE URL:",
            response.url
        )

        print(
            "🌐 OSRM CONTENT TYPE:",
            response.headers.get(
                "Content-Type"
            )
        )

        # ----------------------------------------------------
        # NON-200 RESPONSE
        # ----------------------------------------------------

        if response.status_code != 200:

            print(
                "\n" + "=" * 60
            )

            print(
                "❌ OSRM HTTP REQUEST FAILED"
            )

            print(
                "HTTP STATUS:",
                response.status_code
            )

            print(
                "RESPONSE HEADERS:"
            )

            print(
                dict(response.headers)
            )

            print(
                "RESPONSE BODY:"
            )

            print(
                response.text[:3000]
            )

            print(
                "=" * 60
            )

            return None

        # ----------------------------------------------------
        # EMPTY RESPONSE
        # ----------------------------------------------------

        if not response.text:

            print(
                "\n" + "=" * 60
            )

            print(
                "❌ OSRM RETURNED AN EMPTY RESPONSE"
            )

            print(
                "=" * 60
            )

            return None

        # ----------------------------------------------------
        # RAW RESPONSE PREVIEW
        # ----------------------------------------------------

        print(
            "\n📦 OSRM RESPONSE PREVIEW:"
        )

        print(
            response.text[:2000]
        )

        # ----------------------------------------------------
        # PARSE JSON
        # ----------------------------------------------------

        try:

            data = response.json()

        except ValueError as e:

            print(
                "\n" + "=" * 60
            )

            print(
                "❌ OSRM RETURNED INVALID JSON"
            )

            print(
                "ERROR TYPE:",
                type(e).__name__
            )

            print(
                "ERROR:",
                repr(e)
            )

            print(
                "RAW RESPONSE:"
            )

            print(
                response.text[:3000]
            )

            print(
                "=" * 60
            )

            return None

        # ----------------------------------------------------
        # LOG OSRM API CODE
        # ----------------------------------------------------

        osrm_code = data.get(
            "code"
        )

        osrm_message = data.get(
            "message"
        )

        print(
            "\n🔎 OSRM API CODE:",
            osrm_code
        )

        if osrm_message:

            print(
                "🔎 OSRM API MESSAGE:",
                osrm_message
            )

        # ----------------------------------------------------
        # OSRM DID NOT RETURN "OK"
        # ----------------------------------------------------

        if osrm_code != "Ok":

            print(
                "\n" + "=" * 60
            )

            print(
                "❌ OSRM API RETURNED NON-OK RESPONSE"
            )

            print(
                "OSRM CODE:",
                osrm_code
            )

            print(
                "OSRM MESSAGE:",
                osrm_message
            )

            print(
                "FULL OSRM RESPONSE:"
            )

            print(
                data
            )

            print(
                "=" * 60
            )

            return None

        # ----------------------------------------------------
        # GET ROUTES
        # ----------------------------------------------------

        routes = data.get(
            "routes",
            []
        )

        print(
            "\n🔀 OSRM ROUTES RETURNED:",
            len(routes)
        )

        # ----------------------------------------------------
        # NO ROUTES
        # ----------------------------------------------------

        if not routes:

            print(
                "\n" + "=" * 60
            )

            print(
                "❌ OSRM RETURNED NO ROUTES"
            )

            print(
                "OSRM CODE:",
                osrm_code
            )

            print(
                "FULL RESPONSE:"
            )

            print(
                data
            )

            print(
                "=" * 60
            )

            return None

        # ====================================================
        # SELECT SHORTEST ROAD DISTANCE
        # ====================================================

        valid_routes = []

        for index, candidate_route in enumerate(
            routes
        ):

            distance_meters = candidate_route.get(
                "distance"
            )

            duration_seconds = candidate_route.get(
                "duration"
            )

            print(
                f"\n🛣️ ROUTE {index + 1}"
            )

            print(
                "Distance meters:",
                distance_meters
            )

            print(
                "Duration seconds:",
                duration_seconds
            )

            if distance_meters is None:

                print(
                    "⚠️ Route has no distance. Skipping."
                )

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

            except (
                TypeError,
                ValueError
            ) as e:

                print(
                    "⚠️ Invalid route distance:",
                    repr(e)
                )

                continue

        # ----------------------------------------------------
        # NO VALID ROUTES
        # ----------------------------------------------------

        if not valid_routes:

            print(
                "\n" + "=" * 60
            )

            print(
                "❌ NO VALID ROUTE DISTANCES RETURNED"
            )

            print(
                "=" * 60
            )

            return None

        # ----------------------------------------------------
        # SORT BY ROAD DISTANCE
        # ----------------------------------------------------

        valid_routes.sort(
            key=lambda item: item[0]
        )

        # ----------------------------------------------------
        # SELECT SHORTEST ROUTE
        # ----------------------------------------------------

        shortest_distance_meters = (
            valid_routes[0][0]
        )

        selected_route_index = (
            valid_routes[0][1]
        )

        route = valid_routes[0][2]

        print(
            "\n🏁 SELECTED ROUTE INDEX:",
            selected_route_index
        )

        # ----------------------------------------------------
        # PRINT ALL VALID ROUTES
        # ----------------------------------------------------

        print(
            "\n🛣️ AVAILABLE ROUTES:"
        )

        for (
            route_distance,
            route_index,
            _
        ) in valid_routes:

            print(
                f"   Route {route_index + 1}: "
                f"{route_distance / 1000:.2f} km"
            )

        # ====================================================
        # ROAD DISTANCE
        # ====================================================

        road_distance_km = (
            shortest_distance_meters / 1000
        )

        road_distance_km = round(
            road_distance_km,
            2
        )

        # ====================================================
        # CAR ETA
        # ====================================================

        duration_seconds = route.get(
            "duration"
        )

        if duration_seconds is not None:

            try:

                car_eta_minutes = max(
                    1,
                    round(
                        float(duration_seconds) / 60
                    )
                )

            except (
                TypeError,
                ValueError
            ):

                car_eta_minutes = None

        else:

            car_eta_minutes = None

        # ====================================================
        # ROUTE GEOMETRY
        # ====================================================

        geometry = route.get(
            "geometry"
        )

        if geometry:

            print(
                "\n🗺️ SELECTED ROUTE GEOMETRY: AVAILABLE"
            )

        else:

            print(
                "\n⚠️ SELECTED ROUTE GEOMETRY: MISSING"
            )

        # ====================================================
        # ROUTE STEPS
        # ====================================================

        legs = route.get(
            "legs",
            []
        )

        steps = []

        if legs:

            first_leg = legs[0]

            if isinstance(
                first_leg,
                dict
            ):

                steps = first_leg.get(
                    "steps",
                    []
                )

        print(
            "🧭 SELECTED ROUTE STEPS:",
            len(steps)
        )

        # ====================================================
        # FINAL ROUTE INFORMATION
        # ====================================================

        print(
            "\n" + "=" * 60
        )

        print(
            "✅ OSRM ROUTING SUCCESS"
        )

        print(
            "🛣️ Shortest road distance:",
            road_distance_km,
            "km"
        )

        print(
            "🚗 Car ETA:",
            car_eta_minutes,
            "minutes"
        )

        print(
            "🗺️ Geometry:",
            "AVAILABLE"
            if geometry
            else "MISSING"
        )

        print(
            "🧭 Steps:",
            len(steps)
        )

        print(
            "🔀 Total routes:",
            len(routes)
        )

        print(
            "🏁 Selected route:",
            selected_route_index + 1
        )

        print(
            "=" * 60
        )

        # ====================================================
        # RETURN ROUTE
        # ====================================================

        return {

            "road_distance_km":
                road_distance_km,

            "car_eta_minutes":
                car_eta_minutes,

            "geometry":
                geometry,

            "steps":
                steps,

            "route_count":
                len(routes),

            "selected_route_index":
                selected_route_index
        }

    # ========================================================
    # TIMEOUT
    # ========================================================

    except requests.exceptions.Timeout as e:

        print(
            "\n" + "=" * 60
        )

        print(
            "❌ OSRM REQUEST TIMED OUT"
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            repr(e)
        )

        print(
            "TIMEOUT:",
            ROUTING_TIMEOUT,
            "seconds"
        )

        print(
            "=" * 60
        )

        return None

    # ========================================================
    # CONNECTION / NETWORK ERROR
    # ========================================================

    except requests.exceptions.ConnectionError as e:

        print(
            "\n" + "=" * 60
        )

        print(
            "❌ OSRM CONNECTION ERROR"
        )

        print(
            "This usually indicates a network/DNS/"
            "SSL/outbound connection problem."
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            repr(e)
        )

        print(
            "=" * 60
        )

        return None

    # ========================================================
    # OTHER REQUEST ERROR
    # ========================================================

    except requests.exceptions.RequestException as e:

        print(
            "\n" + "=" * 60
        )

        print(
            "❌ OSRM REQUEST EXCEPTION"
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            repr(e)
        )

        print(
            "=" * 60
        )

        return None

    # ========================================================
    # UNEXPECTED ERROR
    # ========================================================

    except Exception as e:

        print(
            "\n" + "=" * 60
        )

        print(
            "❌ OSRM UNEXPECTED ERROR"
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            repr(e)
        )

        print(
            "=" * 60
        )

        return None


# ============================================================
# BIKE ETA
# ============================================================

def calculate_bike_eta(
    distance_km
):

    if distance_km is None:

        return None

    try:

        eta = (
            float(distance_km)
            /
            BIKE_AVERAGE_SPEED_KMH
        ) * 60

        return max(
            1,
            round(eta)
        )

    except Exception as e:

        print(
            "=" * 60
        )

        print(
            "❌ BIKE ETA CALCULATION ERROR"
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            repr(e)
        )

        print(
            "=" * 60
        )

        return None


# ============================================================
# BUS ETA
# ============================================================

def calculate_bus_eta(
    distance_km
):

    if distance_km is None:

        return None

    try:

        travel_minutes = (
            float(distance_km)
            /
            BUS_AVERAGE_SPEED_KMH
        ) * 60

        total_minutes = (
            travel_minutes
            +
            BUS_WAITING_MINUTES
        )

        return max(
            5,
            round(total_minutes)
        )

    except Exception as e:

        print(
            "=" * 60
        )

        print(
            "❌ BUS ETA CALCULATION ERROR"
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            repr(e)
        )

        print(
            "=" * 60
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

    print(
        "🛣️ HEMOHUB ROAD ROUTING STARTED"
    )

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
    # OSRM ROAD ROUTE
    # --------------------------------------------------------

    route = get_osrm_route(

        start_latitude,
        start_longitude,

        end_latitude,
        end_longitude
    )

    # --------------------------------------------------------
    # OSRM FAILURE
    # --------------------------------------------------------

    if route is None:

        print(
            "\n" + "=" * 60
        )

        print(
            "❌ ROAD ROUTE UNAVAILABLE"
        )

        print(
            "📏 GPS fallback distance:",
            gps_distance,
            "km"
        )

        print(
            "⚠️ OSRM road distance is unavailable."
        )

        print(
            "⚠️ No road ETA can be calculated."
        )

        print(
            "=" * 60
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
    # BIKE ETA
    # --------------------------------------------------------

    bike_eta = calculate_bike_eta(
        road_distance
    )

    # --------------------------------------------------------
    # BUS ETA
    # --------------------------------------------------------

    bus_eta = calculate_bus_eta(
        road_distance
    )

    # ========================================================
    # FINAL LOGGING
    # ========================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "✅ HEMOHUB ROAD ROUTING SUCCESS"
    )

    print(
        "📍 GPS Geographic Distance:",
        gps_distance,
        "km"
    )

    print(
        "🛣️ Final Shortest Road Distance:",
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
        "AVAILABLE"
        if geometry
        else "MISSING"
    )

    print(
        "🧭 Steps:",
        len(steps)
    )

    print(
        "🔀 Route Count:",
        route.get(
            "route_count"
        )
    )

    print(
        "🏁 Selected Route Index:",
        route.get(
            "selected_route_index"
        )
    )

    print(
        "=" * 60
    )

    # ========================================================
    # RETURN COMPLETE ROUTING DATA
    # ========================================================

    return {

        "gps_distance_km":
            gps_distance,

        "road_distance_km":
            road_distance,

        "car_distance_km":
            road_distance,

        "car_eta_minutes":
            car_eta,

        "bike_distance_km":
            road_distance,

        "bike_eta_minutes":
            bike_eta,

        "bus_distance_km":
            road_distance,

        "bus_eta_minutes":
            bus_eta,

        "bus_waiting_minutes":
            BUS_WAITING_MINUTES,

        "distance_type":
            "Shortest available OSRM road distance",

        "geometry":
            geometry,

        "steps":
            steps,

        "route_count":
            route.get(
                "route_count"
            ),

        "selected_route_index":
            route.get(
                "selected_route_index"
            )
    }


# ============================================================
# COMPATIBILITY FUNCTION
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

        result[
            "road_distance_km"
        ],

        result[
            "car_eta_minutes"
        ]
    )


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

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

        result[
            "road_distance_km"
        ],

        result[
            "bike_eta_minutes"
        ]
    )


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

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

        result[
            "road_distance_km"
        ],

        result[
            "bus_eta_minutes"
        ]
    )

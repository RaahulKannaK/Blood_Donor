// =========================================================
// HEMOHUB - LOCATION SYSTEM
// =========================================================

function getUserLocation() {

    // Check whether browser supports geolocation
    if (!navigator.geolocation) {

        alert("Geolocation is not supported by your browser.");

        return;
    }

    // Request user's current location
    navigator.geolocation.getCurrentPosition(

        function(position) {

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            console.log("Latitude:", latitude);
            console.log("Longitude:", longitude);

            // Send location to Django
            sendLocationToServer(
                latitude,
                longitude
            );
        },

        function(error) {

            if (error.code === error.PERMISSION_DENIED) {

                alert(
                    "Location permission was denied. " +
                    "Please allow location access for HemoHub."
                );

            } else if (error.code === error.POSITION_UNAVAILABLE) {

                alert(
                    "Unable to determine your location."
                );

            } else if (error.code === error.TIMEOUT) {

                alert(
                    "Location request timed out."
                );

            } else {

                alert(
                    "Unable to get your location."
                );
            }
        },

        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}


// =========================================================
// SEND LOCATION TO DJANGO
// =========================================================

function sendLocationToServer(
    latitude,
    longitude
) {

    fetch("/save-location/", {

        method: "POST",

        headers: {

            "Content-Type": "application/json",

            "X-CSRFToken": getCSRFToken()
        },

        body: JSON.stringify({

            latitude: latitude,
            longitude: longitude

        })
    })

    .then(response => response.json())

    .then(data => {

        console.log(
            "Location response:",
            data
        );

    })

    .catch(error => {

        console.error(
            "Location error:",
            error
        );

    });
}


// =========================================================
// GET DJANGO CSRF TOKEN
// =========================================================

function getCSRFToken() {

    const name = "csrftoken=";

    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {

        cookie = cookie.trim();

        if (cookie.startsWith(name)) {

            return cookie.substring(
                name.length
            );
        }
    }

    return "";
}
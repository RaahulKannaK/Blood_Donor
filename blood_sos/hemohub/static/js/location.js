function getUserLocation() {

    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    navigator.geolocation.getCurrentPosition(

        function(position) {

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            const accuracy = position.coords.accuracy;

            console.log("Latitude:", latitude);
            console.log("Longitude:", longitude);
            console.log("Accuracy:", accuracy, "meters");

            sendLocationToServer(
                latitude,
                longitude,
                accuracy
            );
        },

        function(error) {

            if (error.code === error.PERMISSION_DENIED) {
                alert(
                    "Location permission was denied. " +
                    "Please allow location access for HemoHub."
                );
            }

            else if (error.code === error.POSITION_UNAVAILABLE) {
                alert("Unable to determine your location.");
            }

            else if (error.code === error.TIMEOUT) {
                alert("Location request timed out.");
            }

            else {
                alert("Unable to get your location.");
            }
        },

        {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        }
    );
}


function sendLocationToServer(
    latitude,
    longitude,
    accuracy
) {

    fetch("/save-location/", {

        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },

        body: JSON.stringify({
            latitude: latitude,
            longitude: longitude,
            accuracy: accuracy
        })

    })

    .then(response => {

        if (!response.ok) {
            throw new Error(
                "HTTP error " + response.status
            );
        }

        return response.json();
    })

    .then(data => {

        console.log(
            "Location saved:",
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


function getCSRFToken() {

    const name = "csrftoken=";

    const cookies =
        document.cookie.split(";");

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
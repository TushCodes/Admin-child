/**
 * @file Public tracking page map.
 */
document.addEventListener("DOMContentLoaded", function () {
    var mapElement = document.getElementById("map");

    // Exit when the tracking result/map is not present on the page.
    if (!mapElement) {
        return;
    }

    // Leaflet must be loaded globally by the base layout.
    if (typeof L === "undefined") {
        console.error("Leaflet is not loaded. Unable to render tracking map.");
        return;
    }

    // Flask puts map points in data attributes.
    var pickupLat = parseFloat(mapElement.dataset.pickupLat);
    var pickupLng = parseFloat(mapElement.dataset.pickupLng);
    var dropLat = parseFloat(mapElement.dataset.dropLat);
    var dropLng = parseFloat(mapElement.dataset.dropLng);

    if (
        Number.isNaN(pickupLat) ||
        Number.isNaN(pickupLng) ||
        Number.isNaN(dropLat) ||
        Number.isNaN(dropLng)
    ) {
        console.error("Invalid coordinates found in tracking map data attributes.");
        return;
    }

    var pickup = [pickupLat, pickupLng];
    var drop = [dropLat, dropLng];

    // Create the tracking map.
    var map = L.map("map", {
        zoomControl: false,
        scrollWheelZoom: false
    }).setView(pickup, 5);

    L.control.zoom({ position: "bottomright" }).addTo(map);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    // Use simple colored map dots.
    var pickupIcon = L.divIcon({
        className: "",
        html: '<span style="display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;border-radius:999px;background:#62a92a;border:2px solid #dbf7b7;box-shadow:0 0 0 4px rgba(98,169,42,.24);"></span>',
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    });

    var dropIcon = L.divIcon({
        className: "",
        html: '<span style="display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;border-radius:999px;background:#f7a33d;border:2px solid #ffe2b7;box-shadow:0 0 0 4px rgba(247,163,61,.22);"></span>',
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    });

    L.marker(pickup, { icon: pickupIcon }).addTo(map).bindPopup("Pickup Location").openPopup();
    L.marker(drop, { icon: dropIcon }).addTo(map).bindPopup("Drop Location");

    // Draw a basic line from pickup to drop.
    var routeLine = L.polyline([pickup, drop], {
        color: "#8bd136",
        weight: 4,
        opacity: 0.9,
        dashArray: "8, 8"
    }).addTo(map);

    map.fitBounds(routeLine.getBounds());
});

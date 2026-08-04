// Render Map Markers dynamically without hardcoded San Francisco coordinates
function updateMapMarkers(hospitals) {
    if (!map) return;

    // Clear existing markers
    if (window.currentMarkers) {
        window.currentMarkers.forEach(m => map.removeLayer(m));
    }
    window.currentMarkers = [];

    if (!hospitals || hospitals.length === 0) return;

    const bounds = [];

    hospitals.forEach(h => {
        const lat = parseFloat(h.latitude);
        const lng = parseFloat(h.longitude);

        if (!isNaN(lat) && !isNaN(lng)) {
            const marker = L.marker([lat, lng]).addTo(map);
            marker.bindPopup(`<b>${h.name}</b><br>${h.city}, ${h.country}`);
            window.currentMarkers.push(marker);
            bounds.push([lat, lng]);
        }
    });

    // Automatically zoom to the city (e.g. Hyderabad) instead of defaulting to San Francisco
    if (bounds.length === 1) {
        map.flyTo(bounds[0], 13);
    } else if (bounds.length > 1) {
        map.fitBounds(bounds, { padding: [50, 50] });
    }
}
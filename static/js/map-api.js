// Map API Module
// Handles Leaflet map initialization and interaction logic

let map;
let currentMarker;
let selectedLocation = null;

// Initialize Leaflet map
function initMap() {
    map = L.map('map').setView([40.7128, -74.0060], 3);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Add click event to map
    map.on('click', onMapClick);
}

// Handle map click
async function onMapClick(e) {
    const { lat, lng } = e.latlng;
    
    // Update marker
    if (currentMarker) {
        map.removeLayer(currentMarker);
    }
    currentMarker = L.marker([lat, lng]).addTo(map);
    
    // Store selected location
    selectedLocation = { lat, lng };
    
    // Fetch weather data
    await fetchWeather(lat, lng);
    
    // Enable generate button
    document.getElementById('generate-btn').disabled = false;
}

// Try to get user's location
function tryUserLocation() {
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                // Center map on user's location
                map.setView([lat, lng], 10);
                
                // Add marker
                if (currentMarker) {
                    map.removeLayer(currentMarker);
                }
                currentMarker = L.marker([lat, lng]).addTo(map);
                
                // Store selected location
                selectedLocation = { lat, lng };
                
                // Fetch weather data
                await fetchWeather(lat, lng);
                
                // Enable generate button
                document.getElementById('generate-btn').disabled = false;
            },
            (error) => {
                console.log('Geolocation not available or denied:', error);
                // Continue with default location
            }
        );
    }
}

// Search for a location
async function searchLocation() {
    const searchTerm = document.getElementById('location-search').value.trim();
    
    if (!searchTerm) {
        showStatus('Please enter a location to search', 'error');
        return;
    }
    
    showStatus('Searching...', 'loading');
    
    try {
        // Use Nominatim (OpenStreetMap) geocoding API
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchTerm)}&limit=1`
        );
        
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const data = await response.json();
        
        if (data.length === 0) {
            showStatus('Location not found', 'error');
            return;
        }
        
        const location = data[0];
        const lat = parseFloat(location.lat);
        const lng = parseFloat(location.lon);
        
        // Center map on location
        map.setView([lat, lng], 10);
        
        // Update marker
        if (currentMarker) {
            map.removeLayer(currentMarker);
        }
        currentMarker = L.marker([lat, lng]).addTo(map);
        
        // Store selected location
        selectedLocation = { lat, lng };
        
        // Fetch weather data
        await fetchWeather(lat, lng);
        
        // Enable generate button
        document.getElementById('generate-btn').disabled = false;
        
        hideStatus();
    } catch (error) {
        console.error('Search error:', error);
        showStatus('Failed to search location', 'error');
    }
}

// Get selected location
function getSelectedLocation() {
    return selectedLocation;
}

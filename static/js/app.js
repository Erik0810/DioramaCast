// Global variables
let map;
let currentMarker;
let selectedLocation = null;
let weatherData = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    setupEventListeners();
    tryUserLocation();
});

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

// Try to get user's location
function tryUserLocation() {
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
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
                fetchWeather(lat, lng);
                
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

// Setup event listeners
function setupEventListeners() {
    document.getElementById('search-btn').addEventListener('click', searchLocation);
    document.getElementById('location-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchLocation();
        }
    });
    document.getElementById('generate-btn').addEventListener('click', generateDiorama);
    
    // Settings modal listeners
    document.getElementById('settings-toggle-btn').addEventListener('click', openSettingsModal);
    document.getElementById('close-settings').addEventListener('click', closeSettingsModal);
    
    // Close modal when clicking outside
    document.getElementById('settings-modal').addEventListener('click', (e) => {
        if (e.target.id === 'settings-modal') {
            closeSettingsModal();
        }
    });
}

// Open settings modal
function openSettingsModal() {
    const modal = document.getElementById('settings-modal');
    modal.classList.add('show');
}

// Close settings modal
function closeSettingsModal() {
    const modal = document.getElementById('settings-modal');
    modal.classList.remove('show');
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

// Fetch weather data for a location
async function fetchWeather(lat, lng) {
    try {
        const response = await fetch(`/api/weather?lat=${lat}&lon=${lng}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch weather');
        }
        
        const data = await response.json();
        weatherData = data;
        
        displayWeather(data);
    } catch (error) {
        console.error('Weather fetch error:', error);
        showWeatherError();
    }
}

// Display weather data
function displayWeather(data) {
    document.querySelector('.placeholder-text').style.display = 'none';
    document.getElementById('weather-content').style.display = 'flex';
    
    document.getElementById('weather-location').textContent = 
        `${data.location}${data.country ? ', ' + data.country : ''}`;
    document.getElementById('weather-temp').textContent = data.temperature;
    document.getElementById('weather-description').textContent = data.description;
    document.getElementById('weather-feels').textContent = data.feels_like;
    document.getElementById('weather-humidity').textContent = data.humidity;
    document.getElementById('weather-wind').textContent = data.wind_speed;
    document.getElementById('weather-pressure').textContent = data.pressure;
    
    // Set weather icon
    const iconCode = data.icon;
    const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
    document.getElementById('weather-icon').src = iconUrl;
}

// Show weather error
function showWeatherError() {
    document.querySelector('.placeholder-text').style.display = 'flex';
    document.getElementById('weather-content').style.display = 'none';
    document.querySelector('.placeholder-text p').textContent = 
        'Failed to load weather data. Please try again.';
}

// Generate diorama image
async function generateDiorama() {
    if (!selectedLocation || !weatherData) {
        showStatus('Please select a location first', 'error');
        return;
    }
    
    // Disable button during generation
    const generateBtn = document.getElementById('generate-btn');
    generateBtn.disabled = true;
    
    showStatus('Generating your diorama... This may take a moment.', 'loading');
    
    try {
        // Gather settings
        const settings = {
            style: document.getElementById('style-select').value,
            time_of_day: document.getElementById('time-select').value,
            season: document.getElementById('season-select').value
        };
        
        // Prepare request data
        const requestData = {
            location: weatherData.location,
            weather: weatherData.description,
            temperature: weatherData.temperature,
            settings: settings,
            coordinates: selectedLocation
        };
        
        // Call image generation API
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error('Image generation failed');
        }
        
        const data = await response.json();
        
        // Display generated image
        displayGeneratedImage(data);
        
        showStatus('Diorama generated successfully!', 'success');
        
        setTimeout(() => {
            hideStatus();
        }, 3000);
    } catch (error) {
        console.error('Generation error:', error);
        showStatus('Failed to generate diorama. Please try again.', 'error');
    } finally {
        generateBtn.disabled = false;
    }
}

// Display generated image
function displayGeneratedImage(data) {
    document.querySelector('#image-display .placeholder-text').style.display = 'none';
    document.getElementById('image-content').style.display = 'flex';
    
    const imgElement = document.getElementById('generated-image');
    imgElement.src = data.image_url;
    
    const promptElement = document.getElementById('image-prompt');
    promptElement.textContent = `Prompt: ${data.prompt}`;
    
    if (data.message) {
        const messageP = document.createElement('p');
        messageP.textContent = data.message;
        messageP.style.marginTop = '0.5rem';
        messageP.style.fontStyle = 'italic';
        messageP.style.color = 'var(--accent-blue)';
        
        const imageInfo = document.querySelector('.image-info');
        const existingMessage = imageInfo.querySelector('p:last-child');
        if (existingMessage && existingMessage !== promptElement) {
            existingMessage.remove();
        }
        imageInfo.appendChild(messageP);
    }
}

// Show status message
function showStatus(message, type) {
    const statusEl = document.getElementById('generation-status');
    statusEl.textContent = message;
    statusEl.className = `status-message show ${type}`;
}

// Hide status message
function hideStatus() {
    const statusEl = document.getElementById('generation-status');
    statusEl.className = 'status-message';
}

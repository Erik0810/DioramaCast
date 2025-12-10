// Main Application Module
// Coordinates between all modules and initializes the application

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    setupEventListeners();
    tryUserLocation();
});

// Setup event listeners
function setupEventListeners() {
    document.getElementById('search-btn').addEventListener('click', searchLocation);
    document.getElementById('location-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchLocation();
        }
    });
    document.getElementById('generate-btn').addEventListener('click', handleGenerateDiorama);
    
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

// Handle generate diorama button click
function handleGenerateDiorama() {
    const location = getSelectedLocation();
    const weather = getWeatherData();
    generateDiorama(location, weather);
}

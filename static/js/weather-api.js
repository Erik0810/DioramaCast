// Weather API Module
// Handles all weather-related API calls and display logic

let weatherData = null;

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
        return data;
    } catch (error) {
        console.error('Weather fetch error:', error);
        showWeatherError();
        throw error;
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

// Get current weather data
function getWeatherData() {
    return weatherData;
}

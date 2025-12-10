from flask import Flask, render_template, jsonify, request
import os
import requests
from datetime import datetime

app = Flask(__name__)

# Configuration
WEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
IMAGE_API_KEY = os.environ.get('NANABANA_API_KEY', '')

@app.route('/')
def index():
    """Render the main landing page"""
    return render_template('index.html')

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get weather data for a location"""
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    if not lat or not lon:
        return jsonify({'error': 'Latitude and longitude required'}), 400
    
    if not WEATHER_API_KEY:
        return jsonify({'error': 'Weather API key not configured'}), 500
    
    try:
        # Using OpenWeatherMap API
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        weather_data = {
            'location': data.get('name', 'Unknown'),
            'country': data.get('sys', {}).get('country', ''),
            'temperature': round(data.get('main', {}).get('temp', 0)),
            'feels_like': round(data.get('main', {}).get('feels_like', 0)),
            'humidity': data.get('main', {}).get('humidity', 0),
            'description': data.get('weather', [{}])[0].get('description', '').capitalize(),
            'icon': data.get('weather', [{}])[0].get('icon', '01d'),
            'wind_speed': round(data.get('wind', {}).get('speed', 0)),
            'pressure': data.get('main', {}).get('pressure', 0)
        }
        
        return jsonify(weather_data)
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch weather data: {str(e)}'}), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generate image based on location, weather, and settings"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    location = data.get('location', 'unknown location')
    weather = data.get('weather', 'clear sky')
    temperature = data.get('temperature', 20)
    settings = data.get('settings', {})
    
    # Get current date
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Create prompt for image generation using the specified format
    prompt = (
        f'Present a clear, 45° top-down isometric miniature 3D cartoon scene of {location}, '
        f'featuring its most iconic landmarks and architectural elements. '
        f'Use soft, refined textures with realistic PBR materials and gentle, lifelike lighting and shadows. '
        f'Integrate {weather} weather directly into the city environment to create an immersive atmospheric mood. '
        f'Use a clean, minimalistic composition with a soft, solid-colored background. '
        f'At the top-center, place the title "{location}" in large bold text, '
        f'a prominent weather icon beneath it, then the date ({current_date}) (small text) '
        f'and temperature ({temperature}°C) (medium text). '
        f'All text must be centered with consistent spacing, and may subtly overlap the tops of the buildings. '
        f'Square 1000x1000 dimension'
    )
    
    # For now, return a placeholder response
    # You'll need to implement actual Nano Banana Pro API integration
    if not IMAGE_API_KEY:
        # Return a placeholder image URL for demo
        return jsonify({
            'image_url': 'https://via.placeholder.com/1000x1000.png?text=Configure+API+Key',
            'prompt': prompt,
            'message': 'Image API key not configured. This is a placeholder.'
        })
    
    try:
        # TODO: Implement actual Nano Banana Pro API call
        # This is a placeholder implementation
        return jsonify({
            'image_url': 'https://via.placeholder.com/1000x1000.png?text=Image+Generated',
            'prompt': prompt,
            'message': 'Image generation successful'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to generate image: {str(e)}'}), 500

if __name__ == '__main__':
    # Only enable debug mode if explicitly set in environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)

from flask import Flask, render_template, jsonify, request
import os
import requests
from datetime import datetime
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

app = Flask(__name__)

# Configuration
WEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

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
    
    # Check if Gemini API key is configured
    if not GEMINI_API_KEY:
        # Return a placeholder image URL for demo
        return jsonify({
            'image_url': 'https://via.placeholder.com/1000x1000.png?text=Configure+API+Key',
            'prompt': prompt,
            'message': 'Gemini API key not configured. This is a placeholder.'
        })
    
    try:
        # Initialize Gemini client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Generate image using Gemini Imagen
        # Note: Using imagen-3.0-generate-001 which is the stable model
        response = client.models.generate_images(
            model='imagen-4.0-fast-generate',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
            )
        )
        
        # Get the generated image
        generated_image = response.generated_images[0]
        
        # Convert image to base64 for embedding in JSON response
        # The image object should have a direct PIL image attribute
        img_pil = generated_image.image._pil_image
        
        buffered = BytesIO()
        img_pil.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Return the image as a data URL
        image_url = f'data:image/png;base64,{img_str}'
        
        return jsonify({
            'image_url': image_url,
            'prompt': prompt,
            'message': 'Image generation successful'
        })
    except Exception as e:
        # Log the full error for debugging
        app.logger.error(f'Gemini API error: {str(e)}')
        return jsonify({
            'error': f'Failed to generate image: {str(e)}',
            'prompt': prompt,
            'message': 'Check API key configuration and model availability'
        }), 500

if __name__ == '__main__':
    # Only enable debug mode if explicitly set in environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)

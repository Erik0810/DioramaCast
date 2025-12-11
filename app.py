from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import os
import requests
from datetime import datetime
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import logging
from functools import wraps
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
WEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Enable CORS with security settings
# In production, ALLOWED_ORIGINS should be set to specific domains
allowed_origins = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
CORS(app, resources={
    r"/api/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "max_age": 3600
    }
})

# Configure caching
cache_config = {
    'CACHE_TYPE': 'redis' if os.environ.get('REDIS_URL') else 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes default
    'CACHE_KEY_PREFIX': 'dioramacast_'
}

if os.environ.get('REDIS_URL'):
    cache_config['CACHE_REDIS_URL'] = REDIS_URL
    logger.info("Redis caching enabled")
else:
    logger.warning("Redis not configured, using simple in-memory cache")
    
cache = Cache(app, config=cache_config)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri=REDIS_URL if os.environ.get('REDIS_URL') else "memory://",
    strategy="fixed-window",
    enabled=lambda: not app.config.get('TESTING', False)
)

# Connection pooling for requests
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=100,
    pool_maxsize=100,
    max_retries=3,
    pool_block=False
)
session.mount('http://', adapter)
session.mount('https://', adapter)

@app.route('/health')
@limiter.exempt
def health_check():
    """Health check endpoint for load balancers"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/ready')
@limiter.exempt
def readiness_check():
    """Readiness check endpoint - verifies external dependencies"""
    try:
        cache_ready = cache is not None and hasattr(cache, 'cache')
    except Exception:
        cache_ready = False
    
    checks = {
        'weather_api': bool(WEATHER_API_KEY),
        'image_api': bool(GEMINI_API_KEY),
        'cache': cache_ready
    }
    
    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503
    
    return jsonify({
        'status': 'ready' if all_ready else 'not_ready',
        'checks': checks,
        'timestamp': datetime.now().isoformat()
    }), status_code

@app.route('/metrics')
@limiter.limit("10 per minute")
def metrics():
    """Basic metrics endpoint"""
    return jsonify({
        'cache_type': cache_config['CACHE_TYPE'],
        'redis_configured': bool(os.environ.get('REDIS_URL')),
        'timestamp': datetime.now().isoformat()
    })

# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # CSP allows inline scripts needed for the application
    response.headers['Content-Security-Policy'] = "default-src 'self' https:; script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; img-src 'self' data: https: blob:; connect-src 'self' https:;"
    return response

@app.route('/')
def index():
    """Render the main landing page"""
    return render_template('index.html')

@app.route('/api/weather', methods=['GET'])
@limiter.limit("30 per minute")
@cache.cached(timeout=300, query_string=True)  # Cache for 5 minutes based on query params
def get_weather():
    """Get weather data for a location"""
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    if not lat or not lon:
        logger.warning("Weather API called without lat/lon")
        return jsonify({'error': 'Latitude and longitude required'}), 400
    
    # Validate coordinates
    try:
        lat_val = float(lat)
        lon_val = float(lon)
        if not (-90 <= lat_val <= 90) or not (-180 <= lon_val <= 180):
            raise ValueError("Invalid coordinate range")
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid coordinates: lat={lat}, lon={lon}")
        return jsonify({'error': 'Invalid latitude or longitude values'}), 400
    
    if not WEATHER_API_KEY:
        logger.error("Weather API key not configured")
        return jsonify({'error': 'Weather API key not configured'}), 500
    
    try:
        start_time = time.time()
        # Using OpenWeatherMap API with connection pooling
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric'
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        elapsed_time = time.time() - start_time
        logger.info(f"Weather API call completed in {elapsed_time:.2f}s for {lat},{lon}")
        
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
    except requests.Timeout:
        logger.error(f"Weather API timeout for {lat},{lon}")
        return jsonify({'error': 'Weather service timeout, please try again'}), 504
    except requests.HTTPError as e:
        logger.error(f"Weather API HTTP error: {e.response.status_code}")
        return jsonify({'error': f'Weather service error: {e.response.status_code}'}), 502
    except requests.RequestException as e:
        logger.error(f"Weather API request failed: {str(e)}")
        return jsonify({'error': 'Failed to fetch weather data, please try again'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in weather API: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/api/generate-image', methods=['POST'])
@limiter.limit("10 per hour;2 per minute")  # Stricter limits for expensive operations
def generate_image():
    """Generate image based on location, weather, and settings"""
    try:
        data = request.get_json()
    except Exception as e:
        logger.warning(f"Invalid JSON in image generation request: {str(e)}")
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    if not data:
        logger.warning("Image generation called with no data")
        return jsonify({'error': 'No data provided'}), 400
    
    location = data.get('location', 'unknown location')
    weather = data.get('weather', 'clear sky')
    temperature = data.get('temperature', 20)
    settings = data.get('settings', {})
    
    # Input validation
    if not isinstance(location, str) or len(location) > 100:
        return jsonify({'error': 'Invalid location parameter'}), 400
    if not isinstance(weather, str) or len(weather) > 100:
        return jsonify({'error': 'Invalid weather parameter'}), 400
    try:
        temp_val = float(temperature)
        if not (-100 <= temp_val <= 100):
            raise ValueError("Temperature out of range")
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid temperature parameter'}), 400
    
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
        logger.warning("Image generation attempted without API key")
        # Return a placeholder image URL for demo
        return jsonify({
            'image_url': 'https://via.placeholder.com/1000x1000.png?text=Configure+API+Key',
            'prompt': prompt,
            'message': 'Gemini API key not configured. This is a placeholder.'
        })
    
    try:
        start_time = time.time()
        logger.info(f"Starting image generation for {location}")
        
        # Initialize Gemini client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Generate image using Gemini Imagen with timeout handling
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                candidate_count=1,  # Use this instead of number_of_images
                image_config=types.ImageConfig(  # Correct class name
                    aspect_ratio="1:1"
                )
            )
        )
        
        # --- CHANGED PROCESSING SECTION ---

        # 1. Locate the image part in the response
        # The response structure is: candidates -> content -> parts
        image_part = response.candidates[0].content.parts[0]
        
        # 2. Extract raw bytes and mime type
        # The image is stored in 'inline_data'
        if image_part.inline_data:
            image_bytes = image_part.inline_data.data
            mime_type = image_part.inline_data.mime_type  # usually "image/jpeg" or "image/png"
        
            # 3. Convert directly to base64
            # No need for BytesIO or PIL here unless you need to edit the image
            img_str = base64.b64encode(image_bytes).decode('utf-8')
        
            # 4. Create the Data URL
            image_url = f'data:{mime_type};base64,{img_str}'
            
            elapsed_time = time.time() - start_time
            logger.info(f"Image generation completed in {elapsed_time:.2f}s for {location}")
        
        else:
            # Fallback if no image was generated (e.g. safety block)
            logger.warning(f"No image generated for {location}. Check safety ratings.")
            image_url = None
        
        return jsonify({
            'image_url': image_url,
            'prompt': prompt,
            'message': 'Image generation successful'
        })
    except Exception as e:
        # Log the full error for debugging
        logger.error(f'Gemini API error for {location}: {str(e)}')
        return jsonify({
            'error': f'Failed to generate image: {str(e)}',
            'prompt': prompt,
            'message': 'Check API key configuration and model availability'
        }), 500

# Error handlers
@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    logger.warning(f"Rate limit exceeded: {get_remote_address()}")
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({
        'error': 'An unexpected error occurred',
        'message': 'Please try again later'
    }), 500

if __name__ == '__main__':
    # Only enable debug mode if explicitly set in environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    logger.info(f"Starting DioramaCast in {'DEBUG' if debug_mode else 'PRODUCTION'} mode")
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)

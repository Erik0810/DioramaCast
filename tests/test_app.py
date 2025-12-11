"""
Test suite for DioramaCast application
Tests basic functionality and API endpoints
"""
import pytest
import json
import os
from app import app, cache, limiter


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    # Set TESTING mode before creating client
    app.config['TESTING'] = True
    
    # Disable limiter for testing by disabling it on the extension
    limiter.enabled = False
    
    with app.test_client() as client:
        yield client
    
    # Re-enable limiter after tests
    limiter.enabled = True


def test_main_page_loads(client):
    """Test that the main page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'DioramaCast' in response.data
    assert b'Generate Beautiful Dioramas' in response.data


def test_weather_api_endpoint(client):
    """Test weather API endpoint structure"""
    response = client.get('/api/weather?lat=40.7128&lon=-74.0060')
    assert response.status_code in [200, 500]  # 500 if no API key configured
    
    data = json.loads(response.data)
    # Should either return weather data or an error message
    assert 'error' in data or 'location' in data


def test_weather_api_missing_params(client):
    """Test weather API with missing parameters"""
    response = client.get('/api/weather')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data


def test_image_generation_endpoint(client):
    """Test image generation API endpoint"""
    payload = {
        'location': 'Test City',
        'weather': 'sunny',
        'temperature': 25,
        'settings': {
            'style': 'realistic',
            'time_of_day': 'midday',
            'season': 'summer'
        }
    }
    
    response = client.post(
        '/api/generate-image',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Should return a prompt and image_url
    assert 'prompt' in data
    assert 'image_url' in data
    
    # Verify prompt contains required elements
    prompt = data['prompt']
    assert 'Test City' in prompt
    assert 'sunny' in prompt
    assert '25°C' in prompt
    assert '1000x1000' in prompt
    assert '45° top-down isometric' in prompt


def test_image_generation_missing_data(client):
    """Test image generation with no JSON data"""
    response = client.post(
        '/api/generate-image',
        data=None,
        content_type='application/json'
    )
    
    # Flask returns 400 for malformed JSON
    assert response.status_code == 400


def test_image_generation_with_defaults(client):
    """Test image generation uses defaults for missing fields"""
    payload = {
        'location': 'Test City'
        # weather, temperature, settings will use defaults
    }
    
    response = client.post(
        '/api/generate-image',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'prompt' in data
    
    # Should use defaults
    prompt = data['prompt']
    assert 'Test City' in prompt
    assert 'clear sky' in prompt  # default weather
    assert '20°C' in prompt  # default temperature


def test_prompt_format():
    """Test that the prompt format is correct"""
    from app import app as flask_app
    
    with flask_app.test_client() as client:
        payload = {
            'location': 'Paris',
            'weather': 'rainy',
            'temperature': 15,
            'settings': {}
        }
        
        response = client.post(
            '/api/generate-image',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        prompt = data['prompt']
        
        # Verify all required components
        required_elements = [
            'Present a clear, 45° top-down isometric miniature 3D cartoon scene',
            'Paris',
            'rainy',
            '15°C',
            'soft, refined textures with realistic PBR materials',
            'gentle, lifelike lighting and shadows',
            'clean, minimalistic composition',
            'soft, solid-colored background',
            'Square 1000x1000 dimension'
        ]
        
        for element in required_elements:
            assert element in prompt, f"Missing required element: {element}"


def test_environment_variables():
    """Test that environment variables can be accessed"""
    # These should be accessible (may be empty strings)
    weather_key = os.environ.get('OPENWEATHER_API_KEY', '')
    image_key = os.environ.get('GEMINI_API_KEY', '')
    
    # Just verify we can read them (they might be empty in local dev)
    assert isinstance(weather_key, str)
    assert isinstance(image_key, str)
    
    print(f"Environment check: Weather API {'configured' if weather_key else 'not set'}")
    print(f"Environment check: Image API {'configured' if image_key else 'not set'}")


def test_gemini_api_key_handling():
    """Test that the app handles Gemini API key correctly"""
    from app import app as flask_app
    
    with flask_app.test_client() as client:
        # Save original environment variable
        original_key = os.environ.get('GEMINI_API_KEY')
        
        # Test without API key - should return placeholder
        os.environ.pop('GEMINI_API_KEY', None)
        
        # Need to reload the app module to pick up the environment change
        import importlib
        import app as app_module
        importlib.reload(app_module)
        
        with app_module.app.test_client() as test_client:
            payload = {
                'location': 'Test City',
                'weather': 'sunny',
                'temperature': 25,
                'settings': {}
            }
            
            response = test_client.post(
                '/api/generate-image',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Should return a placeholder when no API key is configured
            assert 'image_url' in data
            assert 'prompt' in data
            assert 'message' in data or 'placeholder' in data.get('image_url', '').lower()
        
        # Restore original environment variable
        if original_key:
            os.environ['GEMINI_API_KEY'] = original_key
        
        # Reload app module again to restore state
        importlib.reload(app_module)


def test_gemini_api_configuration():
    """Test that app.py correctly reads GEMINI_API_KEY environment variable"""
    from app import GEMINI_API_KEY
    
    # Verify the app module reads the correct environment variable
    expected_key = os.environ.get('GEMINI_API_KEY', '')
    assert GEMINI_API_KEY == expected_key
    
    print(f"GEMINI_API_KEY from app.py: {'[SET]' if GEMINI_API_KEY else '[NOT SET]'}")


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] == 'healthy'
    assert 'timestamp' in data


def test_readiness_endpoint(client):
    """Test readiness check endpoint"""
    response = client.get('/ready')
    # Can be 200 or 503 depending on API key configuration
    assert response.status_code in [200, 503]
    
    data = json.loads(response.data)
    assert 'status' in data
    assert 'checks' in data
    assert 'timestamp' in data
    
    # Verify checks structure
    checks = data['checks']
    assert 'weather_api' in checks
    assert 'image_api' in checks
    assert 'cache' in checks


def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    response = client.get('/metrics')
    # Can be 200 or 429 (rate limited)
    assert response.status_code in [200, 429]
    
    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'cache_type' in data
        assert 'timestamp' in data


def test_security_headers(client):
    """Test that security headers are present"""
    response = client.get('/')
    
    # Check for security headers
    assert 'X-Content-Type-Options' in response.headers
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    
    assert 'X-Frame-Options' in response.headers
    assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
    
    assert 'X-XSS-Protection' in response.headers
    
    assert 'Strict-Transport-Security' in response.headers
    
    assert 'Content-Security-Policy' in response.headers


def test_cors_headers(client):
    """Test CORS headers on API endpoints"""
    response = client.options('/api/weather')
    
    # CORS headers should be present
    assert 'Access-Control-Allow-Origin' in response.headers


def test_weather_input_validation(client):
    """Test input validation for weather endpoint"""
    # Test with invalid latitude
    response = client.get('/api/weather?lat=invalid&lon=-74.0060')
    assert response.status_code == 400
    
    # Test with out-of-range coordinates
    response = client.get('/api/weather?lat=91&lon=-74.0060')
    assert response.status_code == 400
    
    response = client.get('/api/weather?lat=40.7128&lon=181')
    assert response.status_code == 400


def test_image_generation_input_validation(client):
    """Test input validation for image generation"""
    # Test with oversized location string
    payload = {
        'location': 'x' * 200,  # Too long
        'weather': 'sunny',
        'temperature': 25
    }
    response = client.post(
        '/api/generate-image',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 400
    
    # Test with invalid temperature
    payload = {
        'location': 'Test City',
        'weather': 'sunny',
        'temperature': 150  # Out of range
    }
    response = client.post(
        '/api/generate-image',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 400


def test_cache_configuration():
    """Test that cache is properly configured"""
    assert cache is not None
    assert cache.config['CACHE_TYPE'] in ['redis', 'simple']
    assert cache.config['CACHE_KEY_PREFIX'] == 'dioramacast_'


def test_rate_limiter_configuration():
    """Test that rate limiter is properly configured"""
    assert limiter is not None


def test_404_handler(client):
    """Test 404 error handler"""
    response = client.get('/nonexistent-endpoint')
    assert response.status_code == 404
    
    data = json.loads(response.data)
    assert 'error' in data

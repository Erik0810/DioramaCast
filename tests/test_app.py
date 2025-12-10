"""
Test suite for DioramaCast application
Tests basic functionality and API endpoints
"""
import pytest
import json
import os
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


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
    image_key = os.environ.get('NANABANA_API_KEY', '')
    
    # Just verify we can read them (they might be empty in local dev)
    assert isinstance(weather_key, str)
    assert isinstance(image_key, str)
    
    print(f"Environment check: Weather API {'configured' if weather_key else 'not set'}")
    print(f"Environment check: Image API {'configured' if image_key else 'not set'}")

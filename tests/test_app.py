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

def test_api_info_page_loads(client):
    """Test that the API info page loads successfully"""
    response = client.get('/api-info')
    assert response.status_code == 200
    assert b'API Status' in response.data
    assert b'The API is in production' in response.data


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

def test_image_generation_missing_data(client):
    """Test image generation with no JSON data"""
    response = client.post(
        '/api/generate-image',
        data=None,
        content_type='application/json'
    )
    
    # Flask returns 400 for malformed JSON
    assert response.status_code == 400

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

def test_gemini_api_configuration():
    """Test that app.py correctly reads GEMINI_API_KEY environment variable"""
    from app import GEMINI_API_KEY
    
    # Verify the app module reads the correct environment variable
    expected_key = os.environ.get('GEMINI_API_KEY', '')
    assert GEMINI_API_KEY == expected_key
    
    print(f"GEMINI_API_KEY from app.py: {'[SET]' if GEMINI_API_KEY else '[NOT SET]'}")

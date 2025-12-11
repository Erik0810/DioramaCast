"""
Load testing script for DioramaCast application
Uses Locust framework to simulate thousands of concurrent users

Install: pip install locust
Run: locust -f load_test.py --host https://dioramacast.app
Access UI at: http://localhost:8089
"""

from locust import HttpUser, task, between, events
import random
import json

# Sample coordinates for major cities
CITIES = [
    {"lat": 40.7128, "lon": -74.0060, "name": "New York"},
    {"lat": 51.5074, "lon": -0.1278, "name": "London"},
    {"lat": 48.8566, "lon": 2.3522, "name": "Paris"},
    {"lat": 35.6762, "lon": 139.6503, "name": "Tokyo"},
    {"lat": -33.8688, "lon": 151.2093, "name": "Sydney"},
    {"lat": 37.7749, "lon": -122.4194, "name": "San Francisco"},
    {"lat": 52.5200, "lon": 13.4050, "name": "Berlin"},
    {"lat": 55.7558, "lon": 37.6173, "name": "Moscow"},
    {"lat": 19.4326, "lon": -99.1332, "name": "Mexico City"},
    {"lat": -23.5505, "lon": -46.6333, "name": "São Paulo"}
]

WEATHER_CONDITIONS = [
    "clear sky", "few clouds", "scattered clouds", "broken clouds",
    "shower rain", "rain", "thunderstorm", "snow", "mist"
]


class DioramaCastUser(HttpUser):
    """
    Simulates a typical user browsing and using DioramaCast
    """
    # Wait between 1-5 seconds between tasks (realistic user behavior)
    wait_time = between(1, 5)
    
    def on_start(self):
        """Called when a user starts - simulate landing on the page"""
        self.client.get("/")
    
    @task(20)
    def get_weather_cached(self):
        """
        Get weather for a popular location (high probability of cache hit)
        Weight: 20 (most common operation)
        """
        city = random.choice(CITIES[:5])  # Top 5 cities
        with self.client.get(
            f"/api/weather?lat={city['lat']}&lon={city['lon']}",
            name="/api/weather [cached]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.failure("Rate limited")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(5)
    def get_weather_random(self):
        """
        Get weather for a random location (likely cache miss)
        Weight: 5
        """
        city = random.choice(CITIES)
        # Add some randomness to coordinates to simulate different locations
        lat = city['lat'] + random.uniform(-0.5, 0.5)
        lon = city['lon'] + random.uniform(-0.5, 0.5)
        
        with self.client.get(
            f"/api/weather?lat={lat}&lon={lon}",
            name="/api/weather [random]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.failure("Rate limited")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def generate_image(self):
        """
        Generate an image (expensive operation)
        Weight: 1 (less common, more expensive)
        """
        city = random.choice(CITIES)
        weather = random.choice(WEATHER_CONDITIONS)
        temperature = random.randint(-10, 35)
        
        payload = {
            "location": city['name'],
            "weather": weather,
            "temperature": temperature,
            "settings": {
                "style": "realistic",
                "time_of_day": random.choice(["dawn", "midday", "sunset", "night"]),
                "season": random.choice(["spring", "summer", "fall", "winter"])
            }
        }
        
        with self.client.post(
            "/api/generate-image",
            json=payload,
            name="/api/generate-image",
            catch_response=True,
            timeout=60  # Image generation can take longer
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if 'image_url' in data:
                    response.success()
                else:
                    response.failure("No image URL in response")
            elif response.status_code == 429:
                response.failure("Rate limited (expected for image generation)")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(30)
    def health_check(self):
        """
        Health check endpoint (simulates monitoring)
        Weight: 30 (very lightweight, frequent)
        """
        with self.client.get("/health", name="/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(2)
    def get_metrics(self):
        """
        Get application metrics
        Weight: 2
        """
        with self.client.get("/metrics", name="/metrics", catch_response=True) as response:
            if response.status_code in [200, 429]:  # 429 is expected due to rate limit
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")


class HeavyUser(HttpUser):
    """
    Simulates a heavy user who generates many images
    Use sparingly to test rate limiting
    """
    wait_time = between(0.5, 2)
    weight = 1  # Weight relative to other users (DioramaCastUser has implicit weight of 10)
    
    @task(10)
    def generate_images_rapidly(self):
        """Generate images rapidly to test rate limiting"""
        city = random.choice(CITIES)
        payload = {
            "location": city['name'],
            "weather": random.choice(WEATHER_CONDITIONS),
            "temperature": random.randint(-10, 35),
            "settings": {}
        }
        
        with self.client.post(
            "/api/generate-image",
            json=payload,
            name="/api/generate-image [heavy]",
            catch_response=True,
            timeout=60
        ) as response:
            if response.status_code == 429:
                # Expected - rate limiting working
                response.success()
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")


class APIHealthMonitor(HttpUser):
    """
    Simulates monitoring tools checking health endpoints
    """
    wait_time = between(5, 10)
    weight = 1  # Few monitoring instances
    
    @task
    def monitor_health(self):
        """Check health endpoint"""
        self.client.get("/health")
    
    @task
    def monitor_readiness(self):
        """Check readiness endpoint"""
        self.client.get("/ready")


# Event listeners for reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts"""
    print("\n" + "="*60)
    print("DioramaCast Load Test Starting")
    print("="*60)
    print("\nTest Scenarios:")
    print("  - Normal users: Browsing and occasional image generation")
    print("  - Heavy users: Rapid image generation (10% of users)")
    print("  - Monitors: Health check automation")
    print("\nExpected Behavior:")
    print("  - Weather API: Fast responses (cached)")
    print("  - Image generation: Rate limited (10/hour, 2/min)")
    print("  - Health checks: Always fast")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops"""
    print("\n" + "="*60)
    print("DioramaCast Load Test Complete")
    print("="*60)
    print("\nKey Metrics to Review:")
    print("  1. Response times (should be <500ms for weather)")
    print("  2. Error rate (should be <1% excluding rate limits)")
    print("  3. Rate limit effectiveness (429 responses)")
    print("  4. Cache performance (hit rate in logs)")
    print("="*60 + "\n")


# Quick test scenarios
class QuickTest(HttpUser):
    """
    Quick smoke test - just hit the main endpoints once
    Run with: locust -f load_test.py --headless -u 10 -r 5 -t 30s --only-summary QuickTest
    """
    wait_time = between(1, 2)
    
    @task
    def smoke_test(self):
        """Hit all major endpoints once"""
        # Home page
        self.client.get("/")
        
        # Health check
        self.client.get("/health")
        
        # Weather API
        self.client.get("/api/weather?lat=40.7128&lon=-74.0060")
        
        # Metrics
        self.client.get("/metrics")

from locust import HttpUser, task, between
import random
import json

class WeatherAPIUser(HttpUser):
    """
    Simulated user for load testing the Weather API.
    This class defines the behavior of virtual users during load testing.
    """
    
    # Wait between 1 and 5 seconds between tasks
    wait_time = between(1, 5)
    
    # List of cities to use in requests
    cities = ["Paris", "London", "Berlin", "Madrid", "Rome", "New York", "Tokyo", "Sydney"]
    
    @task(3)
    def get_current_weather(self):
        """
        Task to test the current weather endpoint.
        Weight: 3 (higher frequency)
        """
        city = random.choice(self.cities)
        with self.client.get(f"/api/v1/weather/current/{city}", catch_response=True) as response:
            if response.status_code == 200:
                # Validate response format
                data = response.json()
                if "city" not in data or "temperature" not in data:
                    response.failure("Invalid response format")
            elif response.status_code == 404:
                # It's okay if some cities are not found
                pass
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(2)
    def get_forecast(self):
        """
        Task to test the forecast endpoint.
        Weight: 2 (medium frequency)
        """
        city = random.choice(self.cities)
        days = random.choice([3, 5, 7])
        with self.client.get(f"/api/v1/weather/forecast/{city}?days={days}", catch_response=True) as response:
            if response.status_code == 200:
                # Validate response format
                data = response.json()
                if "city" not in data or "forecast_items" not in data:
                    response.failure("Invalid response format")
                elif len(data["forecast_items"]) < days:
                    response.failure(f"Expected {days} forecast items, got {len(data['forecast_items'])}")
            elif response.status_code == 404:
                # It's okay if some cities are not found
                pass
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(1)
    def get_history(self):
        """
        Task to test the history endpoint.
        Weight: 1 (lower frequency)
        """
        city = random.choice(self.cities)
        days = random.choice([3, 5, 7])
        with self.client.get(f"/api/v1/weather/history/{city}?days={days}", catch_response=True) as response:
            if response.status_code == 200:
                # Validate response format
                data = response.json()
                if "city" not in data or "historical_data" not in data:
                    response.failure("Invalid response format")
            elif response.status_code == 404:
                # It's okay if some cities are not found
                pass
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(4)
    def health_check(self):
        """
        Task to test the health check endpoint.
        Weight: 4 (highest frequency - this is a critical endpoint)
        """
        with self.client.get("/api/v1/health/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Health check failed with status code: {response.status_code}")
            else:
                data = response.json()
                if data["status"] != "ok":
                    response.failure(f"Health check returned non-ok status: {data['status']}")

# To run this load test:
# locust -f tests/locustfile.py --host=http://localhost:8000

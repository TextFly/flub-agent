import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_weather(city: str) -> dict:
    """
    Get current weather for a given city
    
    Args:
        city (str): Name of the city to check weather for
        
    Returns:
        dict: Weather information containing temperature, condition, etc.
        
    Raises:
        ValueError: If WEATHER_API_KEY is not set
        requests.exceptions.RequestException: If the API request fails
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise ValueError("WEATHER_API_KEY environment variable is not set")
        
    base_url = "http://api.weatherapi.com/v1/current.json"
    
    # Make the request
    response = requests.get(
        base_url,
        params={
            "key": api_key,
            "q": city
        }
    )
    
    # Raise an exception for bad status codes
    response.raise_for_status()
    
    # Return the weather data
    return response.json()

# Example usage:
# weather_data = check_weather("London")
# print(f"Temperature: {weather_data['current']['temp_c']}°C")
# print(f"Condition: {weather_data['current']['condition']['text']}")

import os
import requests
from urllib.parse import quote
from .base import Tool, ToolParameter

# OpenWeatherMap API key
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def _get_weather_function(**kwargs):
    """Get real weather data from OpenWeatherMap API
    
    Arguments:
        location (str): City name (required) - can also use 'city' parameter
        units (str): Temperature units - 'metric' (Celsius), 'imperial' (Fahrenheit), or 'kelvin'
        lang (str): Language code for weather description (e.g., 'en', 'fr', 'es')
    
    Returns:
        str: Weather information or error message
    """
    location = kwargs.get('location', kwargs.get('city', ''))
    units = kwargs.get('units', 'metric')
    lang = kwargs.get('lang', 'en')
    
    if not location:
        return "Error: location or city parameter is required"
    
    if not WEATHER_API_KEY:
        return "Weather API key not configured. Please set OPENWEATHER_API_KEY environment variable."
    
    try:
        # URL encode the location
        encoded_location = quote(location)
        
        # API endpoint
        url = f"https://api.openweathermap.org/data/2.5/weather?q={encoded_location}&appid={WEATHER_API_KEY}&units={units}&lang={lang}"
        
        # Make API request
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract weather information
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            # Format temperature unit
            unit_symbol = '°C' if units == 'metric' else '°F' if units == 'imperial' else 'K'
            
            return f"Weather in {location}: {description}, Temperature: {temp}{unit_symbol} (feels like: {feels_like}{unit_symbol}), Humidity: {humidity}%, Wind: {wind_speed} m/s"
        elif response.status_code == 401:
            return "Invalid API key. Please check your OPENWEATHER_API_KEY environment variable."
        elif response.status_code == 404:
            return f"City '{location}' not found. Please check the city name and try again."
        else:
            return f"Unable to get weather for {location}. Error code: {response.status_code}"
            
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

# Create the tool instance with metadata
get_weather = Tool(
    name="get_weather",
    description="Get real-time weather information for any city",
    function=_get_weather_function,
    parameters=[
        ToolParameter(
            name="location",
            type="string",
            description="City name (e.g., 'Paris', 'New York')",
            required=True
        ),
        ToolParameter(
            name="units",
            type="string",
            description="Temperature units: 'metric' (Celsius), 'imperial' (Fahrenheit), or 'kelvin'",
            required=False,
            default="metric"
        ),
        ToolParameter(
            name="lang",
            type="string",
            description="Language code for weather description (e.g., 'en', 'fr', 'es')",
            required=False,
            default="en"
        )
    ]
)